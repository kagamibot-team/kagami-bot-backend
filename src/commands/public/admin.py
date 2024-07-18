from src.base.command_events import OnebotContext
from src.base.db import manual_checkpoint
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchLiteral,
    requireAdmin,
)
from src.common.get_local_ip import get_ip


@listenOnebot()
@requireAdmin()
@matchLiteral("::get-ip")
async def _(ctx: OnebotContext):
    await ctx.reply("\n".join(get_ip()))


@listenOnebot()
@requireAdmin()
@matchLiteral("::manual-save")
async def _(ctx: OnebotContext):
    await manual_checkpoint()
    await ctx.reply("ok")
