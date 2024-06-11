"""
`data` 模块主要用于数据的基本修改，在这里实现一些修改数据库数据的基本逻辑。

未来需要实现，将该模块中所有对数据库的操作全部转移至 `curd` 中。
"""

from nonebot import logger
from nonebot_plugin_orm import AsyncSession, async_scoped_session
from sqlalchemy import select, update

from .crud import *
from .Basics import *


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
]
