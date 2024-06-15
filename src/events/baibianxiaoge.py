import random
from src.common.fast_import import *


@root.listen(PickResult)
@withFreeSession()
async def _(session: AsyncSession, e: PickResult):
    for pick in e.picks:
        if pick.awardName == "百变小哥":
            skins = (
                await session.execute(
                    select(Skin).filter(Skin.applied_award_id == pick.awardId)
                )
            ).scalars()

            skins = [
                skin
                for skin in skins
                if len([o for o in skin.owned_skins if cast(int, o.user_id) == e.uid])
                == 0
            ]

            if len(skins) > 0:
                skin = random.choice(skins)
                udid = await qid2did(session, e.uid)
                await give_skin(session, udid, cast(int, skin.data_id))
                await set_skin(session, udid, cast(int, skin.data_id))
                e.extraMessages.append(f"在这些小哥之中，你抓到了一只 {skin.name}！")
                await session.commit()
            else:
                e.extraMessages.append(
                    "在这些小哥之中，你抓到了一只百变小哥，但是它已经没辙了，只会在你面前装嫩了。"
                )

            break
