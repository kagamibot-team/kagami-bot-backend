from nonebot_plugin_alconna import UniMessage

from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import listenOnebot, matchRegex
from src.common.lang.zh import la
from src.core.unit_of_work import get_unit_of_work


@listenOnebot()
@matchRegex("^(mysp|我有多少薯片)$")
async def _(ctx: OnebotContext, _):
    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        res = await uow.users.get_money(uid)

    await ctx.reply(UniMessage(f"你有 {res} 薯片"))
