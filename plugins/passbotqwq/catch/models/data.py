from nonebot import logger
from nonebot_plugin_orm import async_scoped_session
from sqlalchemy import select, update

from .crud import getAllLevels, getGlobal
from .Basics import (
    Award,
    StorageStats,
    Skin,
    UsedStats,
    Level,
    OwnedSkin,
    UsedSkin,
    User,
)


async def setEveryoneInterval(session: async_scoped_session, interval: float):
    await session.execute(update(User).values(pick_time_delta=interval))
    glob = await getGlobal(session)
    glob.catch_interval = interval


async def addAward(
    session: async_scoped_session, user: User, award: Award, delta: int
) -> int | None:
    aws = (
        await session.execute(
            select(StorageStats)
            .filter(StorageStats.award == award)
            .filter(StorageStats.user == user)
        )
    ).scalar_one_or_none()

    if aws is None:
        aws = StorageStats(
            user=user,
            award=award,
            count=delta,
        )
        session.add(aws)
        await session.flush()
        return None

    aws.count += delta
    return aws.count - delta


async def getPosibilities(session: async_scoped_session, level: Level):
    levels = await getAllLevels(session)
    weightSum = sum([l.weight for l in levels])

    return level.weight / weightSum


async def obtainSkin(session: async_scoped_session, user: User, skin: Skin):
    record = (
        await session.execute(
            select(OwnedSkin)
            .filter(OwnedSkin.user == user)
            .filter(OwnedSkin.skin == skin)
        )
    ).scalar_one_or_none()

    if record is not None:
        return False

    record = OwnedSkin(
        user=user,
        skin=skin,
    )

    session.add(record)
    await session.flush()
    return True


async def deleteSkinOwnership(session: async_scoped_session, user: User, skin: Skin):
    record = (
        await session.execute(
            select(OwnedSkin)
            .filter(OwnedSkin.user == user)
            .filter(OwnedSkin.skin == skin)
        )
    ).scalar_one_or_none()

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


async def hangupSkin(session: async_scoped_session, user: User, skin: Skin | None):
    usingRecord = (
        await session.execute(select(UsedSkin).filter(UsedSkin.user == user))
    ).scalar_one_or_none()

    if skin is not None:
        record = (
            await session.execute(
                select(OwnedSkin)
                .filter(OwnedSkin.user == user)
                .filter(OwnedSkin.skin == skin)
            )
        ).scalar_one_or_none()

        if record is None:
            return False

        if usingRecord is not None:
            await session.delete(usingRecord)

        usingRecord = UsedSkin(
            user=user,
            skin=skin,
        )
        session.add(usingRecord)
        await session.flush()

        return True

    if usingRecord is not None:
        await session.delete(usingRecord)

    return True


async def switchSkin(
    session: async_scoped_session, user: User, skins: list[Skin], award: Award
) -> Skin | None:
    usingRecord = (
        await session.execute(
            select(UsedSkin)
            .filter(UsedSkin.user == user)
            .join(Skin, UsedSkin.skin)
            .filter(Skin.award == award)
        )
    ).scalar_one_or_none()

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

        print(
            f"[WARNING] 用户 {user.data_id} 切换了皮肤，但是没有找到对应的皮肤，已切换为第一个皮肤"
        )
        return skins[0]

    index = skins.index(usingRecord.skin)

    if index == len(skins) - 1:
        await session.delete(usingRecord)
        return None

    usingRecord.skin = skins[index + 1]
    return skins[index + 1]


async def reduceAward(
    session: async_scoped_session, user: User, award: Award, count: int
) -> bool:
    record = (
        await session.execute(
            select(StorageStats)
            .filter(StorageStats.user == user)
            .filter(StorageStats.count == award)
        )
    ).scalar_one_or_none()

    if record is None:
        return False

    if record.count < count:
        return False

    record.count -= count

    stats = (
        await session.execute(
            select(UsedStats)
            .filter(UsedStats.user == user)
            .filter(UsedStats.award == award)
        )
    ).scalar_one_or_none()

    if stats is None:
        stats = UsedStats(user=user, award=award, count=count)
        session.add(stats)
        await session.flush()

        return True

    stats.count += count

    return True


async def resetCacheCount(session: async_scoped_session, count: int):
    await session.execute(update(User).values(pick_max_cache=count))
