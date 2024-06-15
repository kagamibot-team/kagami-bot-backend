import asyncio
import time
from typing import Any, Callable, Coroutine, TypeVar, TypeVarTuple
from arclet.alconna import Alconna, Arparma
from arclet.alconna.typing import TDC

import re

from sqlalchemy.ext.asyncio import AsyncSession
from models.db import get_session
from nonebot import get_driver, logger

from ..logic.admin import isAdmin


from .context import (
    ConsoleContext,
    Context,
    OnebotGroupContext,
    OnebotPrivateContext,
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


def debugOnly():
    def wrapper(func: Callable[[TC], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC):
            if get_driver().env == 'dev':
                return await func(ctx)

        return inner

    return wrapper


def listenGroup(manager: EventManager):
    def wrapper(func: Callable[[OnebotGroupContext], Coroutine[Any, Any, T]]):
        manager.listen(OnebotGroupContext)(func)

    return wrapper


def listenPrivate(manager: EventManager):
    def wrapper(func: Callable[[OnebotPrivateContext], Coroutine[Any, Any, T]]):
        manager.listen(OnebotPrivateContext)(func)

    return wrapper


def listenConsole(manager: EventManager):
    def wrapper(func: Callable[[ConsoleContext], Coroutine[Any, Any, T]]):
        manager.listen(ConsoleContext)(func)

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
            [OnebotGroupContext | OnebotPrivateContext], Coroutine[Any, Any, T]
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


def computeTime(func: Callable[[TCP, *TA], Coroutine[Any, Any, T]]):
    async def wrapper(ctx: TCP, *args: *TA):
        start = time.time()
        msg = await func(ctx, *args)
        logger.debug(f'{func.__name__} 花费了 {time.time() - start} 秒')
        return msg
    
    return wrapper
