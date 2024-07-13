from src.core.unit_of_work import get_unit_of_work
from src.imports import *


@listenOnebot()
@matchLiteral("给小哥不是给")
async def _(ctx: OnebotContext):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        if not await uow.skin_inventory.give(uid, 18):
            await ctx.reply(UniMessage("获取成功！"), ref=True, at=False)
        if not await uow.skin_inventory.select(uid, 18):
            await ctx.reply(UniMessage("切换成功！"), ref=True, at=False)


@listenOnebot()
@matchLiteral("给小哥是给")
async def _(ctx: OnebotContext):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        if await uow.skin_inventory.get_using(uid, 84) is not None:
            await uow.skin_inventory.clear(uid, 84)
            await ctx.reply(UniMessage("切换成功！"), ref=True, at=False)


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

        kbs_info = await uow_get_award_info(uow, 25, sid=37)

        await ctx.send(
            UniMessage()
            .text("发现关键词，三小哥登场！！")
            .image(path=kbs_info.image_path)
        )
