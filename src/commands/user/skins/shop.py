import datetime
import re

from src.base.command_events import MessageContext
from src.base.event.event_dispatcher import EventDispatcher
from src.base.event.event_root import root
from src.base.exceptions import KagamiArgumentException
from src.base.res import KagamiResourceManagers
from src.common.command_deco import (
    kagami_exception_handler,
    limit_no_spam,
    limited,
    match_regex,
    require_admin,
    require_awake,
)
from src.common.data.user import get_user_data
from src.common.dialogue import DialogFrom, get_dialog
from src.common.rd import get_random
from src.common.times import now_datetime, timestamp_to_datetime
from src.core.unit_of_work import UnitOfWork, get_unit_of_work
from src.logic.admin import is_admin
from src.ui.base.render import get_render_pool
from src.ui.types.common import UserData
from src.ui.types.skin_shop import SkinBook, SkinShop, SkinShopBought

dispatcher = EventDispatcher()


def is_in_the_same_week(time1: datetime.datetime, time2: datetime.datetime) -> bool:
    return time1.year == time2.year and time1.isocalendar()[1] == time2.isocalendar()[1]


async def get_current_price_of_skin_pack(uow: UnitOfWork, user: UserData) -> int:
    last_timestamp, this_week_count = await uow.users.get_skin_pack_data(user.uid)
    last_datetime = timestamp_to_datetime(last_timestamp)
    now = now_datetime()

    if now < last_datetime or this_week_count == 0:
        return 0
    if not is_in_the_same_week(last_datetime, now):
        return 0
    return 50 * (2 ** (this_week_count - 1))


async def update_skin_pack_data(
    uow: UnitOfWork, user: UserData, current_time: datetime.datetime | None
) -> None:
    if current_time is None:
        current_time = now_datetime()

    last_timestamp, this_week_count = await uow.users.get_skin_pack_data(user.uid)
    last_datetime = timestamp_to_datetime(last_timestamp)
    if current_time < last_datetime or this_week_count == 0:
        await uow.users.set_skin_pack_data(user.uid, current_time.timestamp(), 1)
        return
    if not is_in_the_same_week(last_datetime, current_time):
        await uow.users.set_skin_pack_data(user.uid, current_time.timestamp(), 1)
        return
    await uow.users.set_skin_pack_data(
        user.uid, current_time.timestamp(), this_week_count + 1
    )


def is_holiday(time: datetime.datetime | None = None) -> bool:
    if time is None:
        time = now_datetime()
    return (time.date() - datetime.date(2023, 1, 1)).days % 7 in (0, 6)


@dispatcher.listen(MessageContext)
@kagami_exception_handler()
@require_admin()    # 暂时是测试阶段所以先加上这一行
@limited
@limit_no_spam
@require_awake
@match_regex(r"^(皮肤商店|pfsd)( noui)?$")
async def shop(ctx: MessageContext, result: re.Match[str]) -> None:
    async with get_unit_of_work() as uow:
        sids = await uow.skins.get_all_sids_can_be_bought()
        infos = [await uow.skins.get_info_v2(sid) for sid in sids]
        infos = sorted(infos, key=lambda info: (-info.level, -info.biscuit_price))

        user = await get_user_data(ctx, uow)
        books = [
            SkinBook(
                do_user_have=await uow.skin_inventory.do_user_have(user.uid, info.sid),
                image=KagamiResourceManagers.xiaoge_low(f"sid_{info.sid}.png").url,
                is_drawable=info.can_draw,
                level=info.level,
                name=info.name,
                price=info.biscuit_price,
            )
            for info in infos
        ]
        biscuits = await uow.biscuit.get(user.uid)
        chips = await uow.chips.get(user.uid)
        jx_possibility = 0.8 if is_holiday() else 0
        dialogs = get_dialog(
            (
                DialogFrom.pifudian_normal_jx
                if get_random().random() < jx_possibility
                else DialogFrom.pifudian_normal_shio
            ),
            {"shop"},
        )
        shop = SkinShop(
            user=user,
            biscuits=biscuits,
            skins=books,
            chips=int(chips),
            skin_pack_price=await get_current_price_of_skin_pack(uow, user),
            dialog=get_random().choice(dialogs),
        )

    if result.group(2) is None or not is_admin(ctx):
        img = await get_render_pool().render("skin_shop", data=shop)
        await ctx.send_image(img)
    elif len(shop.skins) > 0:
        await ctx.send("Elements: \n- " + "\n- ".join(str(s) for s in shop.skins))
    else:
        await ctx.send("没有上架的商品")


@dispatcher.listen(MessageContext)
@kagami_exception_handler()
@limited
@limit_no_spam
@require_awake
@match_regex(r"^(皮肤商店|pfsd) 购?买 (.+)$")
async def buy(ctx: MessageContext, result: re.Match[str]) -> None:
    name = result.group(2)
    assert name is not None

    if name == "皮肤盲盒" or name == "盲盒":
        async with get_unit_of_work() as uow:
            user = await get_user_data(ctx, uow)
            price = await get_current_price_of_skin_pack(uow, user)
            rest_chips = await uow.chips.use(user.uid, price)
            await update_skin_pack_data(uow, user, None)
            await uow.items.give(user.uid, "皮肤盲盒", 1)
            current_count = await uow.items.get(user.uid, "皮肤盲盒")
        data = SkinShopBought(
            user=user,
            rest_money=int(rest_chips),
            cost=price,
            current_count=current_count[0],
            from_award_name=None,
            image=None,
            level=None,
            name="皮肤盲盒",
            unit="薯片",
        )
    else:
        async with get_unit_of_work() as uow:
            user = await get_user_data(ctx, uow)
            sid = await uow.skins.get_sid_strong(name)
            info = await uow.skins.get_info_v2(sid)
            ainfo = await uow.awards.get_info(info.aid)
            if info.biscuit_price <= 0 or not info.can_buy:
                raise KagamiArgumentException(f"皮肤 {info.name} 是非卖品")
            if await uow.skin_inventory.do_user_have(user.uid, sid):
                raise KagamiArgumentException(f"你已经有皮肤 {info.name} 了")
            rest_biscuits = await uow.biscuit.use(user.uid, info.biscuit_price)
            await uow.skin_inventory.give(user.uid, sid)
        data = SkinShopBought(
            user=user,
            rest_money=rest_biscuits,
            cost=info.biscuit_price,
            current_count=None,
            from_award_name=ainfo.name,
            image=KagamiResourceManagers.xiaoge_low(f"sid_{info.sid}.png").url,
            level=info.level,
            name=info.name,
            unit="饼干",
        )

    img = await get_render_pool().render("skin_shop_buy", data=data)
    await ctx.send_image(img)


root.link(dispatcher)
