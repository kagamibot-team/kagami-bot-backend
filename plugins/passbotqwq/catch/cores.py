from dataclasses import dataclass
import itertools
import random
import time

from sqlalchemy import select

from .models.data import addAward
from .models.crud import getAllAvailableLevels, getOrCreateUser
from .models.Basics import Award, AwardCountStorage, UserData

from nonebot_plugin_orm import async_scoped_session


@dataclass
class Pick:
    award: Award
    fromNumber: int
    toNumber: int

    def isNew(self):
        return self.fromNumber == 0

    def delta(self):
        return self.toNumber - self.fromNumber


@dataclass
class PicksResult:
    picks: list[Pick]
    uid: int
    restCount: int
    max_pick: int
    time_delta: float
    pick_calc_time: float

    def counts(self):
        return sum([p.delta() for p in self.picks])


async def pick(session: async_scoped_session, user: UserData) -> list[Award]:
    allAvailableLevels = await getAllAvailableLevels(session)
    level = random.choices(allAvailableLevels, [l.weight for l in allAvailableLevels])[
        0
    ]
    awardsResult = await session.execute(select(Award).filter(Award.level == level))
    return [random.choice([a for a in awardsResult.scalars()])]


def recalcPickTime(user: UserData):
    maxPick = user.pick_max_cache
    timeDelta = user.pick_time_delta
    nowTime = time.time()

    if timeDelta == 0:
        user.pick_count_remain = maxPick
        user.pick_count_last_calculated = nowTime
        return -1

    if user.pick_count_remain >= maxPick:
        user.pick_count_last_calculated = nowTime
        return -1

    countAdd = int((nowTime - user.pick_count_last_calculated) / timeDelta)
    user.pick_count_last_calculated += countAdd * timeDelta
    user.pick_count_remain += countAdd

    if user.pick_count_remain >= maxPick:
        user.pick_count_remain = maxPick
        user.pick_count_last_calculated = nowTime
        return -1

    return user.pick_count_remain - nowTime


def canPickCount(user: UserData):
    recalcPickTime(user)
    return user.pick_count_remain


async def handlePick(session: async_scoped_session, uid: int, maxPickCount: int = 1) -> PicksResult:
    user = await getOrCreateUser(session, uid)

    count = canPickCount(user)

    if maxPickCount > 0:
        count = min(maxPickCount, count)
    else:
        count = count

    pickResult = PicksResult([], uid, user.pick_count_remain - count, user.pick_max_cache, user.pick_time_delta, user.pick_count_last_calculated)

    awards = list(itertools.chain(*[await pick(session, user) for _ in range(count)]))
    awardsDelta: dict[Award, int] = {}

    for award in awards:
        if award.data_id in awardsDelta.keys():
            awardsDelta[award] += 1
        else:
            awardsDelta[award] = 1

    user.pick_count_remain -= count

    for award in awardsDelta:
        oldValue = await addAward(session, user, award, awardsDelta[award]) - awardsDelta[award]

        pickResult.picks.append(Pick(award, oldValue, oldValue + awardsDelta[award]))

    return pickResult
