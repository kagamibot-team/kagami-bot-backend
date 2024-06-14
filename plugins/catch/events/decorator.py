import asyncio
from typing import Any, Callable, Coroutine, TypeVar, TypeVarTuple
from arclet.alconna import Alconna, Arparma
from arclet.alconna.typing import TDC

import re

from nonebot_plugin_orm import AsyncSession, get_session

from ..logic.admin import isAdmin


from .context import (
    ConsoleMessageContext,
    Context,
    OnebotGroupMessageContext,
    OnebotPrivateMessageContext,
    PublicContext,
)
from .manager import EventManager


T = TypeVar("T")
TC = TypeVar("TC", bound=Context, covariant=True)
TCP = TypeVar("TCP", bound=PublicContext, covariant=True)
TA = TypeVarTuple("TA")


def matchAlconna(rule: Alconna[TDC]):
    def wrapper(func: Callable[[TC, Arparma[TDC]], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC):
            result = rule.parse(ctx.getMessage())

            if not result.matched:
                return None

            return await func(ctx, result)

        return inner

    return wrapper


def matchRegex(rule: str):
    def wrapper(func: Callable[[TC, re.Match[str]], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC):
            result = re.fullmatch(rule, ctx.getText())

            if result is None:
                return None

            return await func(ctx, result)

        return inner

    return wrapper


def matchLiteral(text: str):
    def wrapper(func: Callable[[TC], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC):
            if text != ctx.getText():
                return None

            return await func(ctx)

        return inner

    return wrapper


def requireAdmin():
    def wrapper(func: Callable[[TCP, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: TCP, *args: *TA):
            if isAdmin(ctx):
                return await func(ctx, *args)

        return inner

    return wrapper


def listenGroup(manager: EventManager):
    def wrapper(func: Callable[[OnebotGroupMessageContext], Coroutine[Any, Any, T]]):
        manager.listen(OnebotGroupMessageContext)(func)

    return wrapper


def listenPrivate(manager: EventManager):
    def wrapper(func: Callable[[OnebotPrivateMessageContext], Coroutine[Any, Any, T]]):
        manager.listen(OnebotPrivateMessageContext)(func)

    return wrapper


def listenConsole(manager: EventManager):
    def wrapper(func: Callable[[ConsoleMessageContext], Coroutine[Any, Any, T]]):
        manager.listen(ConsoleMessageContext)(func)

    return wrapper


def listenPublic(manager: EventManager):
    def wrapper(func: Callable[[PublicContext], Coroutine[Any, Any, T]]):
        listenGroup(manager)(func)
        listenPrivate(manager)(func)
        listenConsole(manager)(func)

    return wrapper


def listenOnebot(manager: EventManager):
    def wrapper(
        func: Callable[
            [OnebotGroupMessageContext | OnebotPrivateMessageContext], Coroutine[Any, Any, T]
        ]
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
    def wrapper(func: Callable[[AsyncSession, *TA], Coroutine[Any, Any, T]]):
        async def inner(*args: *TA):
            session = get_session()
            async with session.begin():
                return await func(session, *args)

        return inner
    
    return wrapper
