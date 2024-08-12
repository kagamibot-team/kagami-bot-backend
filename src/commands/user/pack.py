from typing import Any

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma

from src.base.command_events import GroupContext
from src.common.decorators.command_decorators import (
    listen_message,
    match_alconna,
    match_regex,
    require_admin,
)
from src.core.unit_of_work import get_unit_of_work
from src.services.pool import PoolService


@listen_message()
@require_admin()
@match_regex("^(小[lL]|xl)?(猎场|lc)$")
async def _(ctx: GroupContext, _):
    message: list[str] = []

    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        max_count = await uow.settings.get_pack_count()
        bought = await uow.user_pack.get_own(uid)
        current = await uow.user_pack.get_using(uid)

        for i in range(1, max_count + 1):
            main_aids = await uow.pack.get_main_aids_of_pack(i)
            linked_aids = await uow.pack.get_linked_aids_of_pack(i)
            count = len(main_aids | linked_aids)
            msg = f"= {i} 号猎场 =\n"
            if i in bought:
                msg += "已购"
            if i == current:
                msg += ";当前"
            msg += f"\n共有 {count} 小哥包含在内。"
            message.append(msg)

    await ctx.reply(f"{'\n\n'.join(message)}")


@listen_message()
@require_admin()
@match_regex("^(猎场|lc)([Uu][Pp])$")
async def _(ctx: GroupContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        pack = await service.get_current_pack(uid)
        upid = await service.get_buyable_pool(pack)
        name = "没有"
        if upid is not None:
            info = await uow.up_pool.get_pool_info(upid)
            name = info.name
        if upid in await uow.up_pool.get_own(uid, pack):
            name += "(已购)"
        if upid == await uow.up_pool.get_using(uid):
            name += "(使用中)"

    await ctx.reply(f"当前 {pack} 号猎场的猎场 Up：{name}")


@listen_message()
@require_admin()
@match_alconna(Alconna("re:(切换|qh)(猎场|lc)", Arg("猎场序号", int, flags=[ArgFlag.OPTIONAL])))
async def _(ctx: GroupContext, res: Arparma[Any]):
    dest = res.query[int]("猎场序号")
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        idx = await service.switch_pack(uid, dest)
    await ctx.reply(f"[测试中]已经切换到 {idx} 号猎场了")


@listen_message()
@require_admin()
@match_alconna(Alconna("购买猎场", Arg("猎场序号", int)))
async def _(ctx: GroupContext, res: Arparma[Any]):
    dest = res.query[int]("猎场序号")
    assert dest is not None
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        await service.buy_pack(uid, dest)
    await ctx.reply(f"[测试中]成功购买了 {dest} 号猎场")


@listen_message()
@require_admin()
@match_regex("^切换(猎场)?[uU][pP]池?$")
async def _(ctx: GroupContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        upid = await service.toggle_up_pool(uid)
    await ctx.reply(f"[测试中]切换了猎场up，UPID={upid}")


@listen_message()
@require_admin()
@match_regex("^购买(猎场)?[uU][pP]池?$")
async def _(ctx: GroupContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        info = await service.buy_up_pool(uid)
    await ctx.reply(f"[测试中]购买了猎场up，INFO={info}")
