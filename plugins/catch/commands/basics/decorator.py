from typing import Any, Awaitable, Callable, TypeVar, cast, TypeVarTuple
from arclet.alconna import Alconna, Arparma
from arclet.alconna.typing import TDC

import re


from ...config import config
from ...events.context import (
    ConsoleMessageContext,
    Context,
    OnebotGroupMessageContext,
    OnebotPrivateMessageContext,
    PublicContext,
)
from ...events.manager import EventManager


T = TypeVar("T")
TC = TypeVar("TC", bound=Context, covariant=True)
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
            result = re.match(rule, ctx.getText())

            if not result:
                return None

            return await func(ctx, result)

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
