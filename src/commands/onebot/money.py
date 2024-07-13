from src.core.unit_of_work import get_unit_of_work
from src.imports import *


@listenOnebot()
@matchRegex("^(mysp|我有多少薯片)$")
async def _(ctx: OnebotContext, _):
    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        res = await uow.users.get_money(uid)

    await ctx.reply(UniMessage(la.msg.mysp.format(f"{int(res)}{la.unit.money}")))
