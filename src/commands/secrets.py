from nonebot_plugin_alconna import UniMessage
from pathlib import Path

from src.base.command_events import GroupContext
from src.common.command_deco import listen_message, match_regex
from src.common.data.awards import get_award_info
from src.core.unit_of_work import get_unit_of_work
from src.services.stats import StatService


@listen_message()
@match_regex(r"[\s\S]*(金|暴力?|([Ss][Ee][Xx]|性))[\s\S]*")
async def _(ctx: GroupContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        if await uow.inventories.get_stats(uid, 155) <= 0:
            return
        if await uow.inventories.get_stats(uid, 87) <= 0:
            return
        if await uow.inventories.get_stats(uid, 141) <= 0:
            return
        if not await uow.skin_inventory.give(uid, 37):
            await ctx.reply(UniMessage("获取成功！"), ref=True, at=False)
        if not await uow.skin_inventory.select(uid, 37):
            await ctx.reply(UniMessage("切换成功！"), ref=True, at=False)

        await StatService(uow).kbs(uid)

        await ctx.send_image(Path("./res/三要素.png"))
