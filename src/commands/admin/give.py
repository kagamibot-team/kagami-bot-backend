from typing import Any

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma

from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
)
from src.core.unit_of_work import get_unit_of_work


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna(["::"], "给薯片", Arg("对方", int), Arg("数量", int)))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    target = res.query("对方")
    number = res.query[int]("数量")
    if target is None or number is None:
        return
    assert isinstance(target, int)

    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(target)
        await uow.users.add_money(uid, number)

    await ctx.reply("给了。", at=False, ref=True)


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna(["::"], "全部给薯片", Arg("数量", int)))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    number = res.query[int]("数量")
    if number is None:
        return

    async with get_unit_of_work() as uow:
        for uid in await uow.users.all_users():
            await uow.users.add_money(uid, number)

    await ctx.reply("给了。", at=False, ref=True)


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "给小哥",
        Arg("对方", int),
        Arg("名称", str),
        Arg("数量", int, flags=[ArgFlag.OPTIONAL]),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    target = res.query("对方")
    name = res.query[str]("名称")
    number = res.query[int]("数量")
    if target is None or name is None:
        return
    assert isinstance(target, int)

    if number is None:
        number = 1

    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(target)
        aid = await uow.awards.get_aid_strong(name)
        await uow.inventories.give(uid, aid, number, False)

    await ctx.reply("给了。", at=False, ref=True)


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "给皮肤",
        Arg("对方", int),
        Arg("名称", str),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    target = res.query[int]("对方")
    name = res.query[str]("名称")

    assert target is not None
    assert name is not None

    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(target)
        sid = await uow.skins.get_sid_strong(name)
        await uow.skin_inventory.give(uid, sid)

    await ctx.reply("给了。", at=False, ref=True)
