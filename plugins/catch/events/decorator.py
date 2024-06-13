import asyncio
from typing import Awaitable, Callable, TypeVar, TypeVarTuple
from arclet.alconna import Alconna, Arparma
from arclet.alconna.typing import TDC

import re

from nonebot_plugin_orm import AsyncSession, get_session


from ..config import config
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
    def wrapper(func: Callable[[TC, Arparma[TDC]], Awaitable[T]]):
        async def inner(ctx: TC):
            result = rule.parse(ctx.getMessage())

            if not result.matched:
                return None

            return await func(ctx, result)

        return inner

    return wrapper


def matchRegex(rule: str):
    def wrapper(func: Callable[[TC, re.Match[str]], Awaitable[T]]):
        async def inner(ctx: TC):
            result = re.fullmatch(rule, ctx.getText())

            if result is None:
                return None

            return await func(ctx, result)

        return inner

    return wrapper


def matchLiteral(text: str):
    def wrapper(func: Callable[[TC, str], Awaitable[T]]):
        async def inner(ctx: TC):
            if text != ctx.getText():
                return None

            return await func(ctx, text)

        return inner

    return wrapper


def requireAdmin():
    def wrapper(func: Callable[[TC, *TA], Awaitable[T]]):
        async def inner(ctx: TC, *args: *TA):
            if isinstance(ctx, ConsoleMessageContext):
                return await func(ctx, *args)

            if isinstance(ctx, OnebotGroupMessageContext):
                if ctx.event.group_id in config.admin_groups:
                    return await func(ctx, *args)

            if isinstance(ctx, OnebotPrivateMessageContext):
                if ctx.event.user_id == config.admin_id:
                    return await func(ctx, *args)

            return None

        return inner

    return wrapper


def listenGroup(manager: EventManager):
    def wrapper(func: Callable[[OnebotGroupMessageContext], Awaitable[T]]):
        manager.listen(OnebotGroupMessageContext)(func)

    return wrapper


def listenPrivate(manager: EventManager):
    def wrapper(func: Callable[[OnebotPrivateMessageContext], Awaitable[T]]):
        manager.listen(OnebotPrivateMessageContext)(func)

    return wrapper


def listenConsole(manager: EventManager):
    def wrapper(func: Callable[[ConsoleMessageContext], Awaitable[T]]):
        manager.listen(ConsoleMessageContext)(func)

    return wrapper


def listenPublic(manager: EventManager):
    def wrapper(func: Callable[[PublicContext], Awaitable[T]]):
        listenGroup(manager)(func)
        listenPrivate(manager)(func)
        listenConsole(manager)(func)

    return wrapper


def listenOnebot(manager: EventManager):
    def wrapper(
        func: Callable[
            [OnebotGroupMessageContext | OnebotPrivateMessageContext], Awaitable[T]
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
    def wrapper(func: Callable[[TCP, AsyncSession, *TA], Awaitable[T]]):
        async def inner(ctx: TCP, *args: *TA):
            sender = ctx.getSenderId()
            if sender is None:
                lock = manager[-1]
            else:
                lock = manager[sender]

            async with lock:
                session = get_session()
                async with session.begin():
                    return await func(ctx, session, *args)

        return inner

    return wrapper


def withFreeSession():
    def wrapper(func: Callable[[AsyncSession, *TA], Awaitable[T]]):
        async def inner(*args: *TA):
            session = get_session()
            async with session.begin():
                return await func(session, *args)

        return inner
    
    return wrapper
