from src.base.command_events import OnebotContext
from src.base.exceptions import KagamiRangeError
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
)
from src.core.unit_of_work import get_unit_of_work

from arclet.alconna import Alconna, Arg, Arparma


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna(["::"], "re:(更改|改变|设置)周期", Arg("interval", int)))
async def _(ctx: OnebotContext, res: Arparma):
    interval = res.query[int]("interval")
    assert interval is not None
    if interval < 0:
        raise KagamiRangeError("周期", "大于0的数", interval)

    async with get_unit_of_work() as uow:
        await uow.settings.set_interval(interval)

    await ctx.reply("ok")
