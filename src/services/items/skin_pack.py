from loguru import logger
from nonebot_plugin_alconna import UniMessage
from pydantic import BaseModel

from src.base.command_events import MessageContext
from src.base.res import KagamiResourceManagers
from src.base.res.resource import IResource
from src.common.data.awards import get_award_info
from src.common.dialogue import DialogFrom, get_dialog
from src.common.rd import get_random
from src.common.times import is_holiday
from src.core.unit_of_work import UnitOfWork
from src.repositories.skin_repository import SkinData
from src.services.items.base import KagamiItem, UseItemArgs
from src.ui.base.render import get_render_pool
from src.ui.types.common import AwardInfo
from src.ui.types.skin_shop import SkinPackOpen


async def choose_random_skin(uow: UnitOfWork) -> int:
    """
    抽取一个随机的皮肤，返回其 ID
    """

    skins_grouped = await uow.skins.get_all_sid_grouped_with_level()
    level = get_random().choices([1, 2, 3, 4], [45, 35, 18, 2])[0]
    skins = skins_grouped[level]
    return get_random().choice(list(skins))


def get_skin_return_biscuits(skin_data: SkinData) -> int:
    """
    获取皮肤需要返还多少饼干
    """

    return skin_data.level * (skin_data.level + 1) // 2


class UseItemSkinPackEvent(BaseModel):
    uid: int
    args: UseItemArgs
    skin_data: SkinData
    remain: int
    biscuit_return: int
    biscuit_current: int
    do_user_have_before: bool
    award_info: AwardInfo
    all_skins_data: list[SkinData]


class ItemSkinPack(KagamiItem[UseItemSkinPackEvent]):
    name: str = "皮肤盲盒"
    description: str = "打开来，你可以获得一个随机的皮肤"
    group: str = "消耗品"
    image: IResource = KagamiResourceManagers.res("皮肤盲盒.png")

    async def can_be_used(self, uow: UnitOfWork, args: UseItemArgs) -> bool:
        return True

    async def use(self, uow: UnitOfWork, args: UseItemArgs):
        args.require_count_range(1, 1)
        args.require_target(False)
        uid = args.user.uid

        remain = await self.use_item_in_db(uow, uid, 1)

        # 抽取随机皮肤
        sid = await choose_random_skin(uow)
        data = await uow.skins.get_info_v2(sid)

        # 计算饼干返利并给予用户皮肤
        biscuits_return = get_skin_return_biscuits(data)
        if do_user_have_before := await uow.skin_inventory.do_user_have(uid, sid):
            biscuits_return *= 2
        else:
            await uow.skin_inventory.give(uid, sid)
        await uow.biscuit.add(uid, biscuits_return)
        biscuit_current = await uow.biscuit.get(uid)

        # 补充信息
        award_info = await get_award_info(uow, data.aid, sid=None)
        all_skins_of_award = await uow.skins.get_all_sids_of_one_award(data.aid)
        all_skins_data = [
            await uow.skins.get_info_v2(sid) for sid in all_skins_of_award
        ]

        evt = UseItemSkinPackEvent(
            uid=uid,
            args=args,
            skin_data=data,
            remain=remain,
            biscuit_return=biscuits_return,
            biscuit_current=biscuit_current,
            do_user_have_before=do_user_have_before,
            award_info=award_info,
            all_skins_data=all_skins_data,
        )

        logger.debug(str(evt))
        return evt

    async def send_use_message(self, ctx: MessageContext, data: UseItemSkinPackEvent):
        jx_possibility = 0.8 if is_holiday(data.args.use_time) else 0
        dialog_from = (
            DialogFrom.pifudian_normal_jx
            if get_random().random() < jx_possibility
            else DialogFrom.pifudian_normal_shio
        )
        dialogs = get_dialog(dialog_from, {"shop"})
        view = SkinPackOpen(
            user=data.args.user,
            dialog=get_random().choice(dialogs),
            image=KagamiResourceManagers.xiaoge_low(
                f"sid_{data.skin_data.sid}.png"
            ).url,
            level=data.skin_data.level,
            skin_award_name=data.award_info.name,
            skin_name=data.skin_data.name,
            biscuit_return=data.biscuit_return,
            biscuit_after=data.biscuit_current,
            do_user_have_before=data.do_user_have_before,
        )

        image = await get_render_pool().render("skin_pack", view)
        await ctx.send(UniMessage.image(raw=image))
