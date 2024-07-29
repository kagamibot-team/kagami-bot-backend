from sqlalchemy import select

from src.base.event.event_root import root
from src.common.data.skins import give_skin, use_skin
from src.common.dataclasses.catch_data import PicksEvent
from src.common.rd import get_random
from src.models.models import Skin, SkinRecord


# 抓到新小哥时，多奖励 20 薯片
@root.listen(PicksEvent)
async def _(e: PicksEvent):
    for _, pick in e.picks.awards.items():
        if pick.beforeStats == 0:
            e.picks.money += 20


# 对百变小哥进行处理
@root.listen(PicksEvent)
async def _(e: PicksEvent):
    session = e.session
    picks = e.picks

    # 百变小哥 ID 为 35
    if 35 in picks.awards.keys():
        if picks.awards[35].beforeStats == 0:
            # 第一次遇到百变小哥不给皮肤
            return

        query = select(Skin.data_id).filter(Skin.award_id == 35)
        skins = (await session.execute(query)).scalars().all()

        query = (
            select(SkinRecord.skin_id)
            .join(Skin, Skin.data_id == SkinRecord.skin_id)
            .filter(Skin.award_id == 35)
            .filter(SkinRecord.user_id == e.uid)
        )
        skins2 = (await session.execute(query)).scalars().all()
        skins = [s for s in skins if s not in skins2]

        if len(skins) == 0:
            return

        skin = get_random().choice(skins)

        await give_skin(session, e.uid, skin)
        await use_skin(session, e.uid, skin)
