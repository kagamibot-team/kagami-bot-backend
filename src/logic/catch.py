from dataclasses import dataclass
import random
import time
from typing import cast

from nonebot import logger
from sqlalchemy import func, select, update

from src.common.data.skins import give_skin, set_skin
from src.common.data.users import qid2did

from src.common.decorators.command_decorators import withFreeSession
from src.common.event_root import root

from src.common.db import AsyncSession
from src.models import *


from .catch_time import calculateTime, getInterval


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


async def _getStorage(session: AsyncSession, uid: int, awardId: int):
    "返回一个用户的小哥库存，如果没有，则立即创建"

    stats = (
        await session.execute(
            select(StorageStats).filter(
                StorageStats.target_user_id == uid,
                StorageStats.target_award_id == awardId,
            )
        )
    ).scalar_one_or_none()

    if not stats:
        stats = StorageStats(target_user_id=uid, target_award_id=awardId, count=0)
        session.add(stats)

    return stats


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

    begin = time.time()
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
    logger.debug("随机选择一个小哥使用了 %f 秒" % (time.time() - begin))

    if award is None:
        logger.warning(f"等级 {level[1]} 没有小哥，这是意料之外的事情")
        return None

    awardId, awardName = award

    begin = time.time()
    awardStorage = await _getStorage(session, uid, awardId)
    logger.debug("查询库存使用了 %f 秒" % (time.time() - begin))

    countBefore = awardStorage.count
    awardStorage.count += 1

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

    begin = time.time()
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
    logger.debug(
        "查询等级表使用了 %f 秒, LENGTH = %d" % (time.time() - begin, len(levels))
    )

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
