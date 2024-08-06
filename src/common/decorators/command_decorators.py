import pathlib
import re
from functools import partial
from typing import Any, Callable, Coroutine, Sequence, TypeVar, TypeVarTuple, Unpack

from arclet.alconna import Alconna, Arparma
from arclet.alconna.exceptions import ArgumentMissing, ParamsUnmatched
from loguru import logger
from nonebot import get_driver
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import GroupContext, OnebotContext, PrivateContext
from src.base.event.event_manager import EventManager
from src.base.event.event_root import root
from src.base.event.event_timer import addInterval, addTimeout
from src.base.exceptions import KagamiCoreException
from src.base.onebot.onebot_events import OnebotStartedContext
from src.logic.admin import isAdmin

T = TypeVar("T")
TC_co = TypeVar("TC_co", bound=OnebotContext, covariant=True)
TA = TypeVarTuple("TA")


def matchAlconna(rule: Alconna[Sequence[Any]]):
    """匹配是否符合 Alconna 规则。

    Args:
        rule (Alconna[UniMessage[Any]]): 输入的 Alconna 规则。
    """

    def wrapper(
        func: Callable[[TC_co, Arparma[Sequence[Any]]], Coroutine[Any, Any, T]]
    ):
        async def inner(ctx: TC_co):
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


def matchRegex(rule: str):
    """匹配是否符合正则表达式。

    Args:
        rule (str): 正则表达式规则。
    """

    def wrapper(func: Callable[[TC_co, re.Match[str]], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC_co):
            if not ctx.is_text_only():
                return

            result = re.fullmatch(rule, ctx.text)

            if result is None:
                return None

            return await func(ctx, result)

        return inner

    return wrapper


def matchLiteral(text: str):
    """匹配消息是否就是指定的文本。

    Args:
        text (str): 指定文本。
    """

    def wrapper(func: Callable[[TC_co], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC_co):
            if not ctx.is_text_only():
                return

            if text != ctx.text:
                return None

            return await func(ctx)

        return inner

    return wrapper


def requireAdmin():
    """限制只有管理员才能执行该命令。"""

    def wrapper(func: Callable[[TC_co, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC_co, *args: Unpack[TA]):
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


def debugOnly():
    """限制只有 DEV 环境下才能执行该命令。"""

    def wrapper(func: Callable[[*TA], Coroutine[Any, Any, T]]):
        async def inner(*args: Unpack[TA]):
            if get_driver().env == "dev":
                return await func(*args)

        return inner

    return wrapper


def listenGroup(manager: EventManager = root):
    """添加群聊的事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """

    def wrapper(func: Callable[[GroupContext], Coroutine[Any, Any, T]]):
        manager.listen(GroupContext)(kagami_exception_handler()(func))

    return wrapper


def listenPrivate(manager: EventManager = root):
    """添加私聊的事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """

    def wrapper(func: Callable[[PrivateContext], Coroutine[Any, Any, T]]):
        manager.listen(PrivateContext)(kagami_exception_handler()(func))

    return wrapper


def listenOnebot(manager: EventManager = root):
    """添加 Onebot 事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """

    def wrapper(
        func: Callable[[GroupContext | PrivateContext], Coroutine[Any, Any, T]]
    ):
        listenGroup(manager)(kagami_exception_handler()(func))
        listenPrivate(manager)(kagami_exception_handler()(func))

    return wrapper


def withLoading(text: str = "请稍候……"):
    """在命令执行时添加加载动画（科  目  三）

    Args:
        text (str, optional): 附带的文本，默认是 "请稍候……"。
    """

    def wrapper(func: Callable[[TC_co, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC_co, *args: Unpack[TA]):
            receipt = await ctx.reply(
                UniMessage().text(text).image(path=pathlib.Path("./res/科目三.gif"))
            )
            try:
                msg = await func(ctx, *args)
                return msg
            finally:
                await receipt.recall()

        return inner

    return wrapper


def interval_at_start(interval: float, skip_first: bool = True):
    """在 Bot 上线时创建定时任务

    Args:
        interval (float): 周期
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


def kagami_exception_handler():
    """
    当有小镜 Bot 内部抛出的 KagamiCoreException 错误时，把错误告知给用户。
    """

    def deco(func: Callable[[TC_co], Coroutine[None, None, T]]):
        async def inner(ctx: TC_co) -> T | None:
            try:
                return await func(ctx)
            except (ArgumentMissing, ParamsUnmatched) as e:
                await ctx.reply(str(e.args))
            except KagamiCoreException as e:
                await ctx.reply(e.message)
            except Exception as e:  #!pylint: disable=W0703
                logger.opt(exception=e).exception(e)
                await ctx.reply(
                    UniMessage().text(
                        f"程序遇到了错误：{repr(e)}\n\n如果持续遇到该错误，请与 PT 联系。肥肠抱歉！！"
                    )
                )

        return inner

    return deco


__all__ = [
    "matchAlconna",
    "matchRegex",
    "matchLiteral",
    "requireAdmin",
    "requireOperatorInGroup",
    "debugOnly",
    "listenGroup",
    "listenPrivate",
    "listenOnebot",
    "withLoading",
    "interval_at_start",
    "timeout_at_start",
]
