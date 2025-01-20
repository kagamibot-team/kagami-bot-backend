from pydantic import BaseModel

from src.base.command_events import MessageContext
from src.common.data.awards import get_award_info
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork
from src.repositories.skin_repository import SkinData
from src.services.items.base import KagamiItem, UseItemArgs
from src.ui.types.common import AwardInfo


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
    do_user_have_before: bool
    award_info: AwardInfo
    all_skins_data: list[SkinData]


class ItemSkinPack(KagamiItem[UseItemSkinPackEvent]):
    name: str = "皮肤盲盒"
    description: str = "打开来，你可以获得一个随机的皮肤"
    group: str = "消耗品"

    async def can_be_used(self, uow: UnitOfWork, uid: int, args: UseItemArgs) -> bool:
        return True

    async def use(self, uow: UnitOfWork, uid: int, args: UseItemArgs):
        args.require_count_range(1, 1)
        args.require_target(False)

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

        # 补充信息
        award_info = await get_award_info(uow, data.aid, sid=None)
        all_skins_of_award = await uow.skins.get_all_sids_of_one_award(data.aid)
        all_skins_data = [
            await uow.skins.get_info_v2(sid) for sid in all_skins_of_award
        ]

        return UseItemSkinPackEvent(
            uid=uid,
            args=args,
            skin_data=data,
            remain=remain,
            biscuit_return=biscuits_return,
            do_user_have_before=do_user_have_before,
            award_info=award_info,
            all_skins_data=all_skins_data,
        )

    async def send_use_message(self, ctx: MessageContext, data: UseItemSkinPackEvent):
        message_parts = [
            "你使用了一个皮肤盲盒，",
            f"获得了 {data.skin_data.name} 皮肤，",
            f"这是一个等级为 {data.skin_data.level} 的皮肤，",
            f"你还有 {data.remain} 个皮肤盲盒，",
        ]

        if data.do_user_have_before:
            message_parts.append(
                f"你之前已经拥有过这个皮肤，所以这次获得的饼干奖励翻倍了！"
            )

        message_parts.append(f"返还了 {data.biscuit_return} 个饼干。")

        await ctx.reply("".join(message_parts))
