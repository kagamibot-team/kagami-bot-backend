"""
`data` 模块主要用于数据的基本修改，在这里实现一些修改数据库数据的基本逻辑。

未来需要实现，将该模块中所有对数据库的操作全部转移至 `curd` 中。
"""

from typing import cast
from nonebot import logger
from nonebot_plugin_orm import AsyncSession, async_scoped_session
from sqlalchemy import select, update
from dataclasses import dataclass
from nonebot_plugin_orm import async_scoped_session
import itertools
import random
import time

from .crud import *
from .models import *


Session = async_scoped_session | AsyncSession


async def setInterval(session: Session, interval: float):
    "设置全局的抓小哥周期"

    await session.execute(update(User).values(pick_time_delta=interval))
    glob = await getGlobal(session)
    glob.catch_interval = interval


async def giveAward(session: Session, user: User, award: Award, delta: int) -> int:
    "给予玩家小哥，返回数据库中原先的值"

    aws = await getStorage(session, user, award)
    aws.count += delta

    return aws.count - delta


async def reduceAward(session: Session, user: User, award: Award, count: int) -> bool:
    "减少玩家的小哥量，返回是否成功"

    record = await getStorage(session, user, award)

    if record.count < count:
        return False

    record.count -= count
    stats = await getUsed(session, user, award)
    stats.count += count
    return True


async def getPosibilities(session: Session, level: Level):
    levels = await getAllLevels(session)
    weightSum = sum([l.weight for l in levels])

    return level.weight / weightSum


async def obtainSkin(session: Session, user: User, skin: Skin):
    record = await getOwnedSkin(session, user, skin)

    if record is not None:
        return False

    record = OwnedSkin(
        user=user,
        skin=skin,
    )

    session.add(record)
    await session.flush()
    return True


async def deleteSkinOwnership(session: Session, user: User, skin: Skin):
    record = await getOwnedSkin(session, user, skin)

    if record is None:
        return False

    await session.delete(record)

    usingRecord = (
        await session.execute(
            select(UsedSkin).filter(UsedSkin.user == user).filter(UsedSkin.skin == skin)
        )
    ).scalar_one_or_none()

    if usingRecord is not None:
        await session.delete(usingRecord)

    return True


async def switchSkin(
    session: Session, user: User, skins: list[Skin], award: Award
) -> Skin | None:
    usingRecord = await getUsedSkin(session, user, award)

    if usingRecord is None:
        usingRecord = UsedSkin(
            user=user,
            skin=skins[0],
        )
        session.add(usingRecord)
        await session.flush()
        return skins[0]

    if usingRecord.skin not in skins:
        usingRecord.skin = skins[0]

        logger.warning(
            f"[WARNING] 用户 {user.data_id} 切换了皮肤，但是没有找到对应的皮肤，已切换为第一个皮肤"
        )
        return skins[0]

    index = skins.index(usingRecord.skin)

    if index == len(skins) - 1:
        await session.delete(usingRecord)
        return None

    usingRecord.skin = skins[index + 1]
    return skins[index + 1]


async def resetCacheCount(session: Session, count: int):
    await session.execute(update(User).values(pick_max_cache=count))


async def getUserStorages(session: Session, user: User):
    "获得一个用户在库存页上展示的全部库存统计"

    return (
        (
            await session.execute(
                select(StorageStats)
                .filter(StorageStats.user == user)
                .filter(StorageStats.count > 0)
                .join(Award, StorageStats.award)
                .join(Level, Award.level)
                .order_by(
                    -Level.sorting_priority,
                    Level.weight,
                    -StorageStats.count,
                    Award.data_id,
                )
            )
        )
        .scalars()
        .all()
    )


async def getUserStoragesByLevel(session: Session, user: User, level: Level):
    _query = (
        select(StorageStats.target_award_id)
        .filter(StorageStats.user == user)
        .join(Award, StorageStats.award)
        .filter(Award.level == level)
    )
    return (await session.execute(_query)).scalars().all()


@dataclass
class Pick:
    award: int
    fromNumber: int
    delta: int
    picks: "PicksResult"
    prize: float

    def isNew(self):
        return self.fromNumber == 0

    async def dbAward(self, session: Session):
        return await getAwardById(session, self.award)


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

    # 专门为了百变小哥添加的字段
    baibianxiaogeOccured: bool = False
    baibianxiaogeSkin: int | None = None

    def counts(self):
        return sum([p.delta for p in self.picks])

    def prizes(self):
        return sum([p.prize for p in self.picks])

    def moneyTo(self):
        return self.money_from + self.prizes()

    async def dbUser(self, session: Session):
        return await getUserById(session, self.udid)


async def pick(session: Session, user: User) -> list[Award]:
    levels = await getAllLevels(session)
    level = random.choices(levels, [l.weight for l in levels])[0]
    awardsResult = await getAllAwardsInLevel(session, level)
    return [random.choice(awardsResult)]


async def recalcPickTime(session: Session, user: User):
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

    return nowTime - user.pick_count_last_calculated


async def canPickCount(session: Session, user: User):
    dt = await recalcPickTime(session, user)
    if dt < 0:
        dt = -1

    return user.pick_count_remain


async def handlePick(
    session: Session, uid: int, maxPickCount: int = 1
) -> PicksResult:
    user = await getUser(session, uid)
    count = await canPickCount(session, user)

    udid = cast(int, user.data_id)

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
        (await getGlobal(session)).catch_interval,
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
        aid = cast(int, award.data_id)
        oldValue = await giveAward(session, user, award, awardsDelta[award])
        dt = award.level.price * awardsDelta[award]

        if oldValue == 0:
            dt += 20

        user.money += dt

        pickResult.picks.append(Pick(aid, oldValue, awardsDelta[award], pickResult, dt))

        # 这里是专门为了百变小哥加的代码
        # 你要知道，我平时不喜欢把和实际数据有关的判断直接写到代码里面
        # 而是尽可能地抽象代码的架构，确保数据和代码之间没有太大的联系
        # 但是，百变小哥需要做特殊的判断，并根据相关的标签给予玩家一定
        # 的皮肤奖励

        if award.name == "百变小哥":
            # allAvailableSkins = (await session.execute(select(SkinTagRelation).filter(
            #     SkinTagRelation.tag == await getTag(session, "皮肤奖励", "百变小哥")
            # ).join(
            #     Skin, SkinTagRelation.skin
            # ).join(
            #     OwnedSkin, Skin.owned_skins
            # ).filter(
            #     OwnedSkin.user == user
            # ))).scalars().all()

            allAvailableSkins = (
                (await session.execute(select(Skin).filter(Skin.award == award)))
                .scalars()
                .all()
            )

            allAvailableSkins = [
                s
                for s in allAvailableSkins
                if len([o for o in s.owned_skins if o.user == user]) == 0
            ]

            pickResult.baibianxiaogeOccured = True

            if len(allAvailableSkins) > 0:
                pickedSkin = random.choice(allAvailableSkins)
                pickResult.baibianxiaogeSkin = cast(int, pickedSkin.data_id)

                await obtainSkin(session, user, pickedSkin)

    return pickResult


async def buy(session: async_scoped_session, user: User, code: str, price: float):
    user.money -= price

    if code == "加上限":
        user.pick_max_cache += 1
        return

    if len(code) > 2 and code[:2] == "皮肤":
        skinName = code[2:]
        skin = await getSkinByName(session, skinName)
        assert skin is not None
        await obtainSkin(session, user, skin)
        return


__all__ = [
    "setInterval",
    "giveAward",
    "reduceAward",
    "getPosibilities",
    "obtainSkin",
    "deleteSkinOwnership",
    "switchSkin",
    "resetCacheCount",
    "getUserStorages",
    "getUserStoragesByLevel",
    "Pick",
    "PicksResult",
    "pick",
    "recalcPickTime",
    "canPickCount",
    "handlePick",
    "buy",
]
