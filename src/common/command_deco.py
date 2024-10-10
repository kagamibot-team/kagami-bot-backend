import asyncio
import re
from functools import partial
from typing import (Any, Callable, Coroutine, Sequence, TypeVar, TypeVarTuple,
                    Unpack)

from arclet.alconna import Alconna, Arparma
from arclet.alconna.exceptions import ArgumentMissing, ParamsUnmatched
from loguru import logger
from nonebot import get_driver
from nonebot.exception import ActionFailed
from nonebot_plugin_alconna import UniMessage
from selenium.common.exceptions import WebDriverException

from src.base.command_events import GroupContext, MessageContext
from src.base.event.event_dispatcher import EventDispatcher
from src.base.event.event_root import root
from src.base.event.event_timer import addInterval, addTimeout
from src.base.exceptions import KagamiCoreException, KagamiStopIteration
from src.base.onebot.onebot_events import OnebotStartedContext
from src.common.config import get_config
from src.common.times import now_datetime
from src.common.webhook import send_webhook
from src.core.unit_of_work import get_unit_of_work
from src.logic.admin import isAdmin

T = TypeVar("T")
TE = TypeVar("TE", bound=MessageContext)
TA = TypeVarTuple("TA")


def match_alconna(rule: Alconna[Sequence[Any]]):
    """匹配是否符合 Alconna 规则。

    Args:
        rule (Alconna[UniMessage[Any]]): 输入的 Alconna 规则。
    """

    def wrapper(func: Callable[[TE, Arparma[Sequence[Any]]], Coroutine[Any, Any, T]]):
        async def inner(ctx: TE):
            try:
                result = rule.parse(ctx.message)
            except SyntaxError as e:
                logger.warning(e)
                return None

            if result.error_info is not None and isinstance(
                result.error_info, (ArgumentMissing, ParamsUnmatched)
            ):
                raise result.error_info

            if not result.matched:
                return None

            return await func(ctx, result)

        return inner

    return wrapper


def match_regex(rule: str):
    """匹配是否符合正则表达式。

    Args:
        rule (str): 正则表达式规则。
    """

    def wrapper(func: Callable[[TE, re.Match[str]], Coroutine[Any, Any, T]]):
        async def inner(ctx: TE):
            if not ctx.is_text_only():
                return

            result = re.fullmatch(rule, ctx.text)

            if result is None:
                return None

            return await func(ctx, result)

        return inner

    return wrapper


def match_literal(text: str):
    """匹配消息是否就是指定的文本。

    Args:
        text (str): 指定文本。
    """

    def wrapper(func: Callable[[TE], Coroutine[Any, Any, T]]):
        async def inner(ctx: TE):
            if not ctx.is_text_only():
                return

            if text != ctx.text:
                return None

            return await func(ctx)

        return inner

    return wrapper


def require_admin():
    """限制只有管理员才能执行该命令。"""

    def wrapper(func: Callable[[TE, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: TE, *args: Unpack[TA]):
            if isAdmin(ctx):
                return await func(ctx, *args)

        return inner

    return wrapper


def requireOperatorInGroup():
    """限制只有小镜是管理员的群才能执行该命令。"""

    def wrapper(func: Callable[[GroupContext, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: GroupContext, *args: Unpack[TA]):
            if await ctx.is_group_admin():
                return await func(ctx, *args)

        return inner

    return wrapper


def debug_only():
    """限制只有 DEV 环境下才能执行该命令。"""

    def wrapper(func: Callable[[*TA], Coroutine[Any, Any, T]]):
        async def inner(*args: Unpack[TA]):
            if get_driver().env == "dev":
                return await func(*args)

        return inner

    return wrapper


def listen_message(manager: EventDispatcher = root, priority: int = 0):
    """添加 Onebot 事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """

    def wrapper(func: Callable[[GroupContext], Coroutine[Any, Any, T]]):
        manager.listen(GroupContext, priority=priority)(
            limit_no_spam(kagami_exception_handler()(func))
        )

    return wrapper


def interval_at_start(interval: float, skip_first: bool = True):
    """在 Bot 上线时创建定时任务

    Args:
        interval (float): 周期，单位秒
        skip_first (bool, optional): 是否跳过第一次执行. Defaults to True.
    """

    def deco(func: Callable[[OnebotStartedContext], Any]):
        @root.listen(OnebotStartedContext)
        async def _(ctx: OnebotStartedContext):
            addInterval(interval, partial(func, ctx), skip_first)

    return deco


def timeout_at_start(timeout: float):
    """在 Bot 上线时创建延时任务

    Args:
        timeout (float): 延时时长
    """

    def deco(func: Callable[[OnebotStartedContext], Any]):
        @root.listen(OnebotStartedContext)
        async def _(ctx: OnebotStartedContext):
            addTimeout(timeout, partial(func, ctx))

    return deco


STATUS = {"ACTION_FAILED_COUNT": 0, "WARNING_MESSAGE_TRIGGERED": False}


def kagami_exception_handler():
    """
    当有小镜 Bot 内部抛出的 KagamiCoreException 错误时，把错误告知给用户。
    """

    def deco(func: Callable[[GroupContext], Coroutine[None, None, T]]):
        async def inner(ctx: GroupContext) -> T | None:
            try:
                return await func(ctx)
            except ArgumentMissing as e:
                await ctx.reply(f"你输入的{str(e)}了哦！", ref=True, at=False)
            except ParamsUnmatched as e:
                await ctx.reply(f"你输入的{str(e)}了哦！", ref=True, at=False)
            except KagamiCoreException as e:
                if len(e.message) > 0:
                    await ctx.reply(e.message, ref=True, at=False)
                if isinstance(e, KagamiStopIteration):
                    raise e from e
            except ActionFailed as e:
                # 此时需要判断是不是被风控了
                STATUS["ACTION_FAILED_COUNT"] += 1
                if (
                    get_config().send_message_fail_report_limit > 0
                    and (
                        STATUS["ACTION_FAILED_COUNT"]
                        > get_config().send_message_fail_report_limit
                    )
                    and get_config().bot_send_message_fail_webhook
                    and not STATUS["WARNING_MESSAGE_TRIGGERED"]
                ):
                    await send_webhook(
                        get_config().bot_send_message_fail_webhook,
                        {"message": "bot_send_message_fail"},
                    )
                    STATUS["WARNING_MESSAGE_TRIGGERED"] = True
                raise e from e
            except WebDriverException as e:
                await ctx.reply("渲染页面的时候出错了！请联系 PT 修复呀！")
                raise e from e
            except Exception as e:  #!pylint: disable=W0703
                await ctx.reply(
                    UniMessage().text(
                        f"程序遇到了错误：{repr(e)}\n\n如果持续遇到该错误，请与 PT 联系。肥肠抱歉！！"
                    )
                )
                raise e from e

        return inner

    return deco


def require_awake(func: Callable[[TE, *TA], Coroutine[Any, Any, T]]):
    """
    需要玩家醒着才能执行的指令
    """

    async def _func(ctx: TE, *args: *TA):
        async with get_unit_of_work(ctx.sender_id) as uow:
            n = now_datetime().timestamp()
            uid = await uow.users.get_uid(ctx.sender_id)
            if await uow.users.get_getup_time(uid) > n:
                return

        await func(ctx, *args)

    return _func


def limited(func: Callable[[TE, *TA], Coroutine[Any, Any, T]]):
    """
    限制了使用范围的功能
    """

    async def _func(ctx: TE, *args: *TA):
        if isinstance(ctx, GroupContext):
            if ctx.group_id in get_config().limited_group:
                return

        await func(ctx, *args)

    return _func


NO_SPAM_LOCKS: dict[int, asyncio.Lock] = {}


def limit_no_spam(func: Callable[[TE, *TA], Coroutine[Any, Any, T]]):
    """
    限制不能够疯狂刷屏的指令
    """

    async def _func(ctx: TE, *arg: *TA):
        if ctx.sender_id not in NO_SPAM_LOCKS:
            NO_SPAM_LOCKS[ctx.sender_id] = asyncio.Lock()

        lock = NO_SPAM_LOCKS[ctx.sender_id]
        if lock.locked():
            return

        async with lock:
            await func(ctx, *arg)

    return _func


__all__ = [
    "match_alconna",
    "match_regex",
    "match_literal",
    "require_admin",
    "requireOperatorInGroup",
    "debug_only",
    "listen_message",
    "interval_at_start",
    "timeout_at_start",
]
