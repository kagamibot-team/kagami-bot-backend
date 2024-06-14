from dataclasses import dataclass
import random
from typing import Any, cast

from nonebot import logger
from sqlalchemy import select

from ..models.data import obtainSkin

from ..events.decorator import withFreeSession

from ..putils.typing import Session
from ..models.models import *
from ..models.crud import *

from ..events.root import root

from .catch_time import calculateTime, timeToNextCatch


@dataclass()
class Pick:
    """
    抓小哥的单个结果
    """

    awardId: int
    awardName: str
    countBefore: int
    countDelta: int
    money: float


@dataclass()
class PickResult:
    picks: list[Pick]
    uid: int
    restPickCount: int
    maxPickCount: int
    timeToNextPick: float
    pickInterval: float

    moneyAfterPick: float

    extraMessages: list[str]


async def _pickAward(session: Session, user: User) -> Pick | None:
    """
    该方法是内部方法，请不要在外部调用。
    抓一次小哥，如果成功则返回 `Pick`，不能够抓则返回 `None`。
    """

    if user.pick_count_remain == 0:
        return None

    levels = await getAllLevels(session)

    if len(levels) == 0:
        logger.warning("没有等级，无法抓小哥")
        return None
    
    level = random.choices(levels, weights=[l.weight for l in levels])[0]
    awards = await getAllAwardsInLevel(session, level)

    if len(awards) == 0:
        logger.warning(f"等级 {level.name} 没有小哥，这是意料之外的事情")
        return None
    
    award = random.choice(awards)

    awardStorage = await getStorage(session, user, award)
    countBefore = awardStorage.count
    awardStorage.count += 1
    user.pick_count_remain -= 1

    moneyDelta = level.price if countBefore > 0 else level.price + 20
    user.money += moneyDelta

    pick = Pick(
        awardId=cast(int, award.data_id),
        awardName=award.name,
        countBefore=countBefore,
        countDelta=1,
        money=moneyDelta,
    )

    return pick


async def pickAwards(session: Session, user: User, count: int) -> PickResult:
    """
    抓 `count` 次小哥，返回抓到的结果。
    """

    await calculateTime(session, user)

    picks: dict[int, Pick] = {}

    i = 0

    while i < count or count < 0:
        pick = await _pickAward(session, user)
        if pick is None:
            break

        if pick.awardId in picks.keys():
            picks[pick.awardId].countDelta += 1
            picks[pick.awardId].money += pick.money
        else:
            picks[pick.awardId] = pick
        
        i += 1
    
    return PickResult(
        picks=list(picks.values()),
        uid=cast(int, user.data_id),
        restPickCount=user.pick_count_remain,
        maxPickCount=user.pick_max_cache,
        timeToNextPick=await timeToNextCatch(session, user),
        pickInterval=(await getGlobal(session)).catch_interval,
        moneyAfterPick=user.money,
        extraMessages=[],
    )


@root.listen(PickResult)
@withFreeSession()
async def _(session: Session, e: PickResult):
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
                if len([o for o in skin.owned_skins if cast(int, o.user_id) == e.uid]) == 0
            ]

            if len(skins) > 0:
                skin = random.choice(skins)
                user = await getUserById(session, e.uid)
                await obtainSkin(session, user, skin)
                await setSkin(session, user, skin)
                e.extraMessages.append(f"在这些小哥之中，你抓到了一只 {skin.name}！")
                await session.commit()
            else:
                e.extraMessages.append("在这些小哥之中，你抓到了一只百变小哥，但是它已经没辙了，只会在你面前装嫩了。")
            
            break
