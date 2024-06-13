import asyncio
import pathlib
from typing import Any, Callable, Coroutine, TypeVar, TypeVarTuple

from nonebot_plugin_alconna import UniMessage

from ...events.context import UniContext


T = TypeVar("T")
TC = TypeVar("TC", bound=UniContext, covariant=True)
TA = TypeVarTuple("TA")


def withLoading(text: str = "请稍候……"):
    def wrapper(func: Callable[[TC, *TA], Coroutine[Any, Any, T]]):
        async def inner(ctx: TC, *args: *TA):
            receipt = await ctx.reply(
                UniMessage()
                .text(text)
                .image(path=pathlib.Path("./res/catch/科目三.gif"))
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
