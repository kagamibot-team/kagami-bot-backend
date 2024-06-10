from dataclasses import dataclass
import itertools
import random
import time

from sqlalchemy import select

from .models.data import addAward, obtainSkin
from .models.crud import getAllAvailableLevels, getGlobal, getOrCreateUser
from .models.Basics import Award, AwardCountStorage, AwardSkin, UserData

from nonebot_plugin_orm import async_scoped_session


@dataclass
class Pick:
    award: int
    fromNumber: int | None
    delta: int
    picks: "PicksResult"
    prize: float

    def isNew(self):
        return self.fromNumber is None


@dataclass
class PicksResult:
    picks: list[Pick]
    uid: int
    udid: int
    restCount: int
    max_pick: int
    time_delta: float
    pick_calc_time: float
    money_from: float

    def counts(self):
        return sum([p.delta for p in self.picks])

    def prizes(self):
        return sum([p.prize for p in self.picks])

    def moneyTo(self):
        return self.money_from + self.prizes()


async def pick(session: async_scoped_session, user: UserData) -> list[Award]:
    allAvailableLevels = await getAllAvailableLevels(session)
    level = random.choices(allAvailableLevels, [l.weight for l in allAvailableLevels])[
        0
    ]
    awardsResult = await session.execute(select(Award).filter(Award.level == level))
    return [random.choice([a for a in awardsResult.scalars()])]


async def recalcPickTime(session: async_scoped_session, user: UserData):
    glob = await getGlobal(session)

    maxPick = user.pick_max_cache
    timeDelta = glob.catch_interval
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


async def canPickCount(session: async_scoped_session, user: UserData):
    await recalcPickTime(session, user)
    return user.pick_count_remain


async def handlePick(
    session: async_scoped_session, uid: int, maxPickCount: int = 1
) -> PicksResult:
    user = await getOrCreateUser(session, uid)
    count = await canPickCount(session, user)

    udid = int(user.data_id)  # type: ignore

    if maxPickCount > 0:
        count = min(maxPickCount, count)
    else:
        count = count

    pickResult = PicksResult(
        [],
        uid,
        udid,
        user.pick_count_remain - count,
        user.pick_max_cache,
        user.pick_time_delta,
        user.pick_count_last_calculated,
        user.money,
    )

    awards = list(itertools.chain(*[await pick(session, user) for _ in range(count)]))
    awardsDelta: dict[Award, int] = {}

    for award in awards:
        if award in awardsDelta.keys():
            awardsDelta[award] += 1
        else:
            awardsDelta[award] = 1

    user.pick_count_remain -= count

    for award in awardsDelta:
        aid = int(award.data_id)  # type: ignore
        oldValue = await addAward(session, user, award, awardsDelta[award])
        dt = award.level.price * awardsDelta[award]

        if oldValue is None:
            dt += 20

        user.money += dt

        pickResult.picks.append(Pick(aid, oldValue, awardsDelta[award], pickResult, dt))

    return pickResult


async def buy(session: async_scoped_session, user: UserData, code: str, price: float):
    user.money -= price

    if code == "加上限":
        user.pick_max_cache += 1
        return

    if len(code) > 2 and code[:2] == "皮肤":
        skinName = code[2:]
        skin = (
            await session.execute(select(AwardSkin).where(AwardSkin.name == skinName))
        ).scalar_one()
        assert skin is not None

        await obtainSkin(session, user, skin)
        return
