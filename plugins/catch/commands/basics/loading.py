import pathlib
from typing import Awaitable, Callable, TypeVar, TypeVarTuple

from nonebot_plugin_alconna import UniMessage

from ...events.context import UniContext


T = TypeVar("T")
TC = TypeVar("TC", bound=UniContext, covariant=True)
TA = TypeVarTuple("TA")


def withLoading(text: str = "请稍候……"):
    def wrapper(func: Callable[[TC, *TA], Awaitable[T]]):
        async def inner(ctx: TC, *args: *TA):
            receipt = await ctx.reply(
                UniMessage()
                .text(text)
                .image(path=pathlib.Path("./res/catch/科目三.gif"))
            )
            msg = await func(ctx, *args)
            await receipt.recall()
            return msg

        return inner

    return wrapper
