from typing import Any

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma

from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    matchRegex,
    requireAdmin,
)
from src.core.unit_of_work import get_unit_of_work
from src.services.pool import PoolService


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna("切换猎场", Arg("猎场序号", int, flags=[ArgFlag.OPTIONAL])))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    dest = res.query[int]("猎场序号")
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        idx = await service.switch_pack(uid, dest)
    await ctx.reply(f"[测试中]已经切换到 {idx} 号猎场了")


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna("购买猎场", Arg("猎场序号", int)))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    dest = res.query[int]("猎场序号")
    assert dest is not None
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        await service.buy_pack(uid, dest)
    await ctx.reply(f"[测试中]成功购买了 {dest} 号猎场")


@listenOnebot()
@requireAdmin()
@matchRegex("^切换(猎场)?[uU][pP]池?$")
async def _(ctx: OnebotContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        upid = await service.toggle_up_pool(uid)
    await ctx.reply(f"[测试中]切换了猎场up，UPID={upid}")


@listenOnebot()
@requireAdmin()
@matchRegex("^购买(猎场)?[uU][pP]池?$")
async def _(ctx: OnebotContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        info = await service.buy_up_pool(uid)
    await ctx.reply(f"[测试中]购买了猎场up，INFO={info}")
