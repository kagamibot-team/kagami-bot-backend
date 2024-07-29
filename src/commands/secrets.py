from nonebot_plugin_alconna import UniMessage

from src.base.command_events import OnebotContext
from src.common.data.awards import get_award_info
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchLiteral,
    matchRegex,
)
from src.core.unit_of_work import get_unit_of_work


@listenOnebot()
@matchLiteral("哇嘎嘎嘎")
async def _(ctx: OnebotContext):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        if await uow.inventories.get_stats(uid, 1) <= 0:
            return
        if await uow.inventories.get_stats(uid, 4) <= 0:
            return
        if not await uow.skin_inventory.give(uid, 31):
            await ctx.reply(UniMessage("获取成功！"), ref=True, at=False)
        if not await uow.skin_inventory.select(uid, 31):
            await ctx.reply(UniMessage("切换成功！"), ref=True, at=False)


@listenOnebot()
@matchRegex(r"[\s\S]*(金|暴力?|([Ss][Ee][Xx]|性))[\s\S]*")
async def _(ctx: OnebotContext, _):
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

        kbs_info = await get_award_info(uow, 25, sid=37)

        await ctx.send(
            UniMessage()
            .text("发现关键词，三小哥登场！！")
            .image(path=kbs_info.image_path)
        )
