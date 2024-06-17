import random
from src.common.fast_import import *


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

        query = select(Skin.data_id).filter(Skin.applied_award_id == 35)
        skins = (await session.execute(query)).scalars().all()

        query = (
            select(OwnedSkin.skin_id)
            .join(Skin, Skin.data_id == OwnedSkin.skin_id)
            .filter(Skin.applied_award_id == 35)
            .filter(OwnedSkin.user_id == e.uid)
        )
        skins2 = (await session.execute(query)).scalars().all()
        skins = [s for s in skins if s not in skins2]

        if len(skins) == 0:
            return

        skin = random.choice(skins)

        await give_skin(session, e.uid, skin)
        await set_skin(session, e.uid, skin)


# 将图片和描述改成皮肤的图片和描述
@root.listen(PrePickMessageEvent)
async def _(e: PrePickMessageEvent):
    for aid, display in e.displays.items():
        query = (
            select(Skin.name, Skin.extra_description, Skin.image)
            .filter(Skin.applied_award_id == aid)
            .filter(Skin.used_skins.any(UsedSkin.user_id == e.uid))
        )
        skin = (await e.session.execute(query)).one_or_none()
        if skin:
            name, description, image = skin.tuple()
            display.name += f"[{name}]"
            display.image = image

            if len(description.strip()) > 0:
                display.description = description
