from typing import Any

from arclet.alconna import Alconna, Arg, Arparma, Option

from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
)
from src.core.unit_of_work import get_unit_of_work


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "猎场设置",
        Option("开放猎场数", Arg("猎场数", int), alias=["猎场数", "-n"]),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    pack_count: int | None = res.query[int]("猎场数")

    async with get_unit_of_work() as uow:
        if pack_count is not None:
            await uow.settings.set_pack_count(pack_count)

    await ctx.reply("ok.")
