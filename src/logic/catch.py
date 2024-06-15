import random
import time

from src.common.fast_import import *
from .catch_time import *


async def _pickAward(
    session: AsyncSession, uid: int, levels: list[tuple[int, str, float, float]]
) -> Pick | None:
    """
    该方法是内部方法，请不要在外部调用。
    抓一次小哥，如果成功则返回 `Pick`，不能够抓则返回 `None`。
    """

    if len(levels) == 0:
        logger.warning("没有等级，无法抓小哥")
        return None

    level = random.choices(levels, weights=[l[2] for l in levels])[0]

    award = (
        await session.execute(
            select(Award.data_id, Award.name)
            .filter(
                Award.level_id == level[0],
            )
            .order_by(func.random())
            .limit(1)
        )
    ).one_or_none()

    if award is None:
        logger.warning(f"等级 {level[1]} 没有小哥，这是意料之外的事情")
        return None

    awardId, awardName = award

    countBefore = await addStorage(session, uid, awardId, 1)

    moneyDelta = level[3] if countBefore > 0 else level[3] + 20

    pick = Pick(
        awardId=awardId,
        awardName=awardName,
        countBefore=countBefore,
        countDelta=1,
        money=moneyDelta,
    )

    return pick


async def pickAwards(session: AsyncSession, uid: int, count: int) -> PickResult:
    """
    抓 `count` 次小哥，返回抓到的结果。
    """

    pick_count_remain, pick_count_last_calculated, maxPickCount = await calculateTime(
        session, uid
    )

    money = (
        await session.execute(select(User.money).filter(User.data_id == uid))
    ).scalar_one()

    levels = [
        l.tuple()
        for l in (
            await session.execute(
                select(Level.data_id, Level.name, Level.weight, Level.price).filter(
                    Level.weight > 0
                )
            )
        ).all()
    ]

    picks: dict[int, Pick] = {}

    i = 0

    while i < count or count < 0:
        if pick_count_remain == 0:
            break

        pick = await _pickAward(session, uid, levels)
        if pick is None:
            break

        if pick.awardId in picks.keys():
            picks[pick.awardId].countDelta += 1
            picks[pick.awardId].money += pick.money
        else:
            picks[pick.awardId] = pick

        i += 1
        pick_count_remain -= 1

    interval = await getInterval(session)

    dm = sum(p.money for p in picks.values())

    await session.execute(
        update(User)
        .where(User.data_id == uid)
        .values(
            pick_count_remain=pick_count_remain,
            money=money + dm,
        )
    )

    return PickResult(
        picks=list(picks.values()),
        uid=uid,
        restPickCount=pick_count_remain,
        maxPickCount=maxPickCount,
        timeToNextPick=pick_count_last_calculated + interval,
        pickInterval=interval,
        moneyAfterPick=money + dm,
        extraMessages=[],
    )
