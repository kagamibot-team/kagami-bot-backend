from typing import Any, Awaitable, Callable, TypeVar, cast
from arclet.alconna import Alconna, Arparma
from arclet.alconna.typing import TDC

import re

from ...events.context import TE, Context


T = TypeVar("T")
TC = TypeVar("TC", bound=Context)


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
