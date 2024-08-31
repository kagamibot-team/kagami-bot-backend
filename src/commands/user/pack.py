from typing import Any

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import MessageContext
from src.common.command_deco import (
    limited,
    listen_message,
    match_alconna,
    match_regex,
    require_admin,
    require_awake,
)
from src.common.data.awards import get_award_info
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork, get_unit_of_work
from src.services.pool import PoolService
from src.services.stats import StatService
from src.ui.base.browser import get_browser_pool
from src.ui.types.liechang import LiechangCountInfo, LiechangData, SingleLiechang
from src.ui.views.pack import (
    get_random_expression,
)
from src.ui.types.common import UserData


async def get_pack_data(uow: UnitOfWork, user: UserData):
    packs: list[SingleLiechang] = []
    uid = user.uid

    for i in range(1, await uow.settings.get_pack_count() + 1):
        aids = await uow.pack.get_main_aids_of_pack(i)
        grouped = await uow.awards.group_by_level(aids)
        grouped = {d: v for d, v in grouped.items() if len(v) > 0}
        top_lid = max(grouped.keys())

        acount = [
            LiechangCountInfo(
                level=uow.levels.get_data_by_id(lid),
                collected=len(
                    [
                        v
                        for _, v in (
                            await uow.inventories.get_inventory_dict(uid, aids)
                        ).items()
                        if sum(v) > 0
                    ]
                ),
                sum_up=len(aids),
            )
            for lid, aids in grouped.items()
            if lid > 0
        ]
        acount = sorted(acount, key=lambda v: v.level.display_name, reverse=True)

        packs.append(
            SingleLiechang(
                pack_id=i,
                award_count=acount,
                featured_award=await get_award_info(
                    uow, list(grouped[top_lid])[0], uid
                ),
                unlocked=i in await uow.user_pack.get_own(uid),
            )
        )

    return LiechangData(
        packs=packs,
        user=user,
        selecting=await uow.user_pack.get_using(uid),
        dialogue=get_random_expression(get_random()),
        chips=int(await uow.money.get(uid)),
    )


@listen_message()
@limited
@match_regex("^(小[鹅lL]|x[le])?(猎场|lc)$")
@require_awake
async def _(ctx: MessageContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        data = await get_pack_data(
            uow,
            UserData(
                uid=uid, qqid=str(ctx.sender_id), name=await ctx.get_sender_name()
            ),
        )
        await StatService(uow).check_lc_view(uid, data.selecting)

    browsers = get_browser_pool()
    img = await browsers.render("liechang", data)

    await ctx.send(UniMessage.image(raw=img))


@listen_message()
@require_admin()
@limited
@match_regex("^(猎场|lc)([Uu][Pp])$")
@require_awake
async def _(ctx: MessageContext, _):
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
@limited
@match_alconna(
    Alconna("re:(切换|qh)(猎场|lc)", Arg("猎场序号", int, flags=[ArgFlag.OPTIONAL]))
)
@require_awake
async def _(ctx: MessageContext, res: Arparma[Any]):
    dest = res.query[int]("猎场序号")
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        await service.switch_pack(uid, dest)
        data = await get_pack_data(
            uow,
            UserData(
                uid=uid, qqid=str(ctx.sender_id), name=await ctx.get_sender_name()
            ),
        )
        await StatService(uow).check_lc_view(uid, data.selecting)
        await StatService(uow).qhlc_command(uid, data.selecting)

    browsers = get_browser_pool()
    img = await browsers.render("liechang", data)

    await ctx.send(UniMessage.image(raw=img))


@listen_message()
@limited
@match_alconna(Alconna("re:(购买|gm|buy)(猎场|lc)", Arg("猎场序号", int)))
@require_awake
async def _(ctx: MessageContext, res: Arparma[Any]):
    dest = res.query[int]("猎场序号")
    assert dest is not None
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        await service.buy_pack(uid, dest)
    await ctx.reply(f"成功购买了 {dest} 号猎场")


@listen_message()
@require_admin()
@match_regex("^切换(猎场)?[uU][pP]池?$")
@require_awake
async def _(ctx: MessageContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        upid = await service.toggle_up_pool(uid)
    await ctx.reply(f"[测试中]切换了猎场up，UPID={upid}")


@listen_message()
@require_admin()
@match_regex("^购买(猎场)?[uU][pP]池?$")
@require_awake
async def _(ctx: MessageContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = PoolService(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        info = await service.buy_up_pool(uid)
    await ctx.reply(f"[测试中]购买了猎场up，INFO={info}")
