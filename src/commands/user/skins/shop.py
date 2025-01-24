import datetime
import re

from src.base.command_events import MessageContext
from src.base.event.event_dispatcher import EventDispatcher
from src.base.event.event_root import root
from src.base.res import KagamiResourceManagers
from src.common.command_deco import (
    kagami_exception_handler,
    limit_no_spam,
    limited,
    match_regex,
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
from src.ui.types.skin_shop import SkinBook, SkinShop

dispatcher = EventDispatcher()


async def get_current_price_of_skin_pack(uow: UnitOfWork, user: UserData) -> int:
    last_timestamp, this_week_count = await uow.users.get_skin_pack_data(user.uid)
    last_datetime = timestamp_to_datetime(last_timestamp)
    now = now_datetime()

    if now < last_datetime or this_week_count == 0:
        return 0
    if (now.date() - last_datetime.date()).days >= 7:
        return 0
    return 50 * (2 ** (this_week_count - 1))


def is_holiday(time: datetime.datetime | None = None) -> bool:
    if time is None:
        time = now_datetime()
    return (time.date() - datetime.date(2023, 1, 1)).days % 7 in (0, 6)


@dispatcher.listen(MessageContext)
@kagami_exception_handler()
@limited
@limit_no_spam
@require_awake
@match_regex(r"^皮肤商店( noui)?$")
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
        jx_possibility = 0.8 if is_holiday() else 0.2
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

    if result.group(1) is None or not is_admin(ctx):
        img = await get_render_pool().render("skin_shop", data=shop)
        await ctx.send_image(img)
    elif len(shop.skins) > 0:
        await ctx.send("Elements: \n- " + "\n- ".join(str(s) for s in shop.skins))
    else:
        await ctx.send("没有上架的商品")


root.link(dispatcher)
