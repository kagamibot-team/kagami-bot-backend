import asyncio
import time
from typing import Any, Callable, Coroutine, TypeVar, TypeVarTuple
from arclet.alconna import Alconna, Arparma

import re

from sqlalchemy.ext.asyncio import AsyncSession
from src.common.db import get_session
from nonebot import get_driver, logger

from src.common.event_root import root

from ...logic.admin import isAdmin


import pathlib
from typing import Any, Callable, Coroutine, TypeVar, TypeVarTuple

from nonebot_plugin_alconna import UniMessage


from ..classes.command_events import (
    ConsoleContext,
    GroupContext,
    PrivateContext,
    PublicContext,
    UniContext,
)
from src.common.classes.event_manager import EventManager


T = TypeVar("T")
TC = TypeVar("TC", bound=UniContext, covariant=True)
TCP = TypeVar("TCP", bound=PublicContext, covariant=True)
TA = TypeVarTuple("TA")


def matchAlconna(rule: Alconna[UniMessage[Any]]):
    """匹配是否符合 Alconna 规则。

    Args:
        rule (Alconna[UniMessage[Any]]): 输入的 Alconna 规则。
    """
    def wrapper(func: Callable[[TC, Arparma[UniMessage[Any]]], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC):
            result = rule.parse(ctx.getMessage())

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
    def wrapper(func: Callable[[TC, re.Match[str]], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC):
            result = re.fullmatch(rule, ctx.getText())

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
    def wrapper(func: Callable[[TC], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC):
            if not ctx.isTextOnly():
                return None
            
            if text != ctx.getText():
                return None

            return await func(ctx)

        return inner

    return wrapper


def requireAdmin():
    """限制只有管理员才能执行该命令。
    """
    def wrapper(func: Callable[[TCP, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: TCP, *args: *TA):
            if isAdmin(ctx):
                return await func(ctx, *args)

        return inner

    return wrapper


def debugOnly():
    """限制只有 DEV 环境下才能执行该命令。
    """
    def wrapper(func: Callable[[TC], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC):
            if get_driver().env == "dev":
                return await func(ctx)

        return inner

    return wrapper


def listenGroup(manager: EventManager = root):
    """添加群聊的事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """
    def wrapper(func: Callable[[GroupContext], Coroutine[Any, Any, T]]):
        manager.listen(GroupContext)(func)

    return wrapper


def listenPrivate(manager: EventManager = root):
    """添加私聊的事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """
    def wrapper(func: Callable[[PrivateContext], Coroutine[Any, Any, T]]):
        manager.listen(PrivateContext)(func)

    return wrapper


def listenConsole(manager: EventManager = root):
    """添加控制台的事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """
    def wrapper(func: Callable[[ConsoleContext], Coroutine[Any, Any, T]]):
        manager.listen(ConsoleContext)(func)

    return wrapper


def listenPublic(manager: EventManager = root):
    """添加全局消息的事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """
    def wrapper(func: Callable[[PublicContext], Coroutine[Any, Any, T]]):
        listenGroup(manager)(func)
        listenPrivate(manager)(func)
        listenConsole(manager)(func)

    return wrapper


def listenOnebot(manager: EventManager = root):
    """添加 Onebot 事件监听器

    Args:
        manager (EventManager, optional): 事件管理器，默认是 root。
    """
    def wrapper(
        func: Callable[[GroupContext | PrivateContext], Coroutine[Any, Any, T]]
    ):
        listenGroup(manager)(func)
        listenPrivate(manager)(func)

    return wrapper


class SessionLockManager:
    dc: dict[int, asyncio.Lock]

    def __init__(self) -> None:
        self.dc = {}

    def __getitem__(self, key: int):
        if key not in self.dc:
            self.dc[key] = asyncio.Lock()
        return self.dc[key]


globalSessionLockManager = SessionLockManager()


def withSessionLock(manager: SessionLockManager = globalSessionLockManager):
    """获得一个异步的 SQLAlchemy 会话，并使用锁来保证线程安全。"""
    def wrapper(func: Callable[[TCP, AsyncSession, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: TCP, *args: *TA):
            # sender = ctx.getSenderId()
            # if sender is None:
            #     lock = manager[-1]
            # else:
            #     lock = manager[sender]
            lock = manager[-1]

            async with lock:
                session = get_session()
                async with session.begin():
                    msg = await func(ctx, session, *args)
                    await session.close()
                    return msg

        return inner

    return wrapper


def withFreeSession():
    """随便获得一个异步的 SQLAlchemy 会话"""

    def wrapper(func: Callable[[AsyncSession, *TA], Coroutine[Any, Any, T]]):
        async def inner(*args: *TA):
            session = get_session()
            async with session.begin():
                return await func(session, *args)

        return inner

    return wrapper


def computeTime(func: Callable[[TCP, *TA], Coroutine[Any, Any, T]]):
    """计算命令执行的时间，并在日志中输出"""
    async def wrapper(ctx: TCP, *args: *TA):
        start = time.time()
        msg = await func(ctx, *args)
        logger.debug(f"{func.__name__} 花费了 {time.time() - start} 秒")
        return msg

    return wrapper


def withLoading(text: str = "请稍候……"):
    """在命令执行时添加加载动画（科  目  三）

    Args:
        text (str, optional): 附带的文本，默认是 "请稍候……"。
    """
    def wrapper(func: Callable[[TC, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC, *args: *TA):
            receipt = await ctx.reply(
                UniMessage().text(text).image(path=pathlib.Path("./res/科目三.gif"))
            )
            try:
                msg = await func(ctx, *args)
                return msg
            except StopIteration as e:
                raise e from e
            except Exception as e:
                await ctx.reply(
                    UniMessage().text(
                        f"程序遇到了错误：{repr(e)}\n\n如果持续遇到该错误，请与 PT 联系。肥肠抱歉！"
                    )
                )

                raise e from e
            finally:
                await receipt.recall()

        return inner

    return wrapper
