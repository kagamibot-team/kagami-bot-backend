from src.base.command_events import MessageContext
from src.base.exceptions import KagamiRangeError
from src.common.command_decorators import (
    listen_message,
    match_alconna,
    require_admin,
)
from src.core.unit_of_work import get_unit_of_work

from arclet.alconna import Alconna, Arg, Arparma


@listen_message()
@require_admin()
@match_alconna(Alconna(["::"], "re:(更改|改变|设置)周期", Arg("interval", int)))
async def _(ctx: MessageContext, res: Arparma):
    interval = res.query[int]("interval")
    assert interval is not None
    if interval < 0:
        raise KagamiRangeError("周期", "大于0的数", interval)

    async with get_unit_of_work() as uow:
        await uow.settings.set_interval(interval)

    await ctx.reply("ok")
