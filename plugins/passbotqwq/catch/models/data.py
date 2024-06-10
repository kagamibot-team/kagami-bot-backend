from nonebot import logger
from nonebot_plugin_orm import async_scoped_session
from sqlalchemy import select, update

from .crud import getAllLevels, getGlobal
from .Basics import (
    Award,
    AwardCountStorage,
    AwardSkin,
    AwardUsedStats,
    Level,
    SkinOwnRecord,
    SkinRecord,
    UserData,
)


async def setEveryoneInterval(session: async_scoped_session, interval: float):
    await session.execute(update(UserData).values(pick_time_delta=interval))
    glob = await getGlobal(session)
    glob.catch_interval = interval


async def addAward(
    session: async_scoped_session, user: UserData, award: Award, delta: int
) -> int | None:
    aws = (
        await session.execute(
            select(AwardCountStorage)
            .filter(AwardCountStorage.target_award == award)
            .filter(AwardCountStorage.target_user == user)
        )
    ).scalar_one_or_none()

    if aws is None:
        aws = AwardCountStorage(
            target_user=user,
            target_award=award,
            award_count=delta,
        )
        session.add(aws)
        await session.flush()
        return None

    aws.award_count += delta
    return aws.award_count - delta


async def getPosibilities(session: async_scoped_session, level: Level):
    levels = await getAllLevels(session)
    weightSum = sum([l.weight for l in levels])

    return level.weight / weightSum


async def obtainSkin(session: async_scoped_session, user: UserData, skin: AwardSkin):
    record = (
        await session.execute(
            select(SkinOwnRecord)
            .filter(SkinOwnRecord.user == user)
            .filter(SkinOwnRecord.skin == skin)
        )
    ).scalar_one_or_none()

    if record is not None:
        return False

    record = SkinOwnRecord(
        user=user,
        skin=skin,
    )

    session.add(record)
    await session.flush()
    return True


async def deleteSkinOwnership(
    session: async_scoped_session, user: UserData, skin: AwardSkin
):
    record = (
        await session.execute(
            select(SkinOwnRecord)
            .filter(SkinOwnRecord.user == user)
            .filter(SkinOwnRecord.skin == skin)
        )
    ).scalar_one_or_none()

    if record is None:
        return False

    await session.delete(record)

    usingRecord = (
        await session.execute(
            select(SkinRecord)
            .filter(SkinRecord.user == user)
            .filter(SkinRecord.skin == skin)
        )
    ).scalar_one_or_none()

    if usingRecord is not None:
        await session.delete(usingRecord)

    return True


async def hangupSkin(
    session: async_scoped_session, user: UserData, skin: AwardSkin | None
):
    usingRecord = (
        await session.execute(select(SkinRecord).filter(SkinRecord.user == user))
    ).scalar_one_or_none()

    if skin is not None:
        record = (
            await session.execute(
                select(SkinOwnRecord)
                .filter(SkinOwnRecord.user == user)
                .filter(SkinOwnRecord.skin == skin)
            )
        ).scalar_one_or_none()

        if record is None:
            return False

        if usingRecord is not None:
            await session.delete(usingRecord)

        usingRecord = SkinRecord(
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
    session: async_scoped_session, user: UserData, skins: list[AwardSkin]
) -> AwardSkin | None:
    usingRecord = (
        await session.execute(select(SkinRecord).filter(SkinRecord.user == user))
    ).scalar_one_or_none()

    if usingRecord is None:
        usingRecord = SkinRecord(
            user=user,
            skin=skins[0],
        )
        session.add(usingRecord)
        await session.flush()
        return skins[0]


    if usingRecord.skin not in skins:
        usingRecord.skin = skins[0]

        print(f"[WARNING] 用户 {user.data_id} 切换了皮肤，但是没有找到对应的皮肤，已切换为第一个皮肤")
        return skins[0]
    
    index = skins.index(usingRecord.skin)
    
    if index == len(skins) - 1:
        await session.delete(usingRecord)
        return None
    
    usingRecord.skin = skins[index + 1]
    return skins[index + 1]


async def reduceAward(
    session: async_scoped_session, user: UserData, award: Award, count: int
) -> bool:
    record = (
        await session.execute(
            select(AwardCountStorage)
            .filter(AwardCountStorage.target_user == user)
            .filter(AwardCountStorage.award_count == award)
        )
    ).scalar_one_or_none()

    if record is None:
        return False

    if record.award_count < count:
        return False

    record.award_count -= count

    stats = (
        await session.execute(
            select(AwardUsedStats)
            .filter(AwardUsedStats.target_user == user)
            .filter(AwardUsedStats.target_award == award)
        )
    ).scalar_one_or_none()

    if stats is None:
        stats = AwardUsedStats(target_user=user, target_award=award, award_count=count)
        session.add(stats)
        await session.flush()

        return True

    stats.award_count += count

    return True


async def resetCacheCount(session: async_scoped_session, count: int):
    await session.execute(update(UserData).values(pick_max_cache=count))
