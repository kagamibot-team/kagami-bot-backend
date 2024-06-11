from sqlalchemy import select
from nonebot_plugin_orm import AsyncSession, async_scoped_session, get_session

from .Basics import Skin, Global, Level, Award, StorageStats, UsedSkin, User


def selectAllLevelUserObtained(user: User):
    return select(Level).filter(
        Level.awards.any(
            Award.storage_stats.any(
                StorageStats.user == user
            )
        )
    )


async def getAllAwards(session: async_scoped_session):
    return (await session.execute(select(Award).filter())).scalars()


async def getAllLevels(session: async_scoped_session):
    return (await session.execute(select(Level).filter())).scalars()


async def getAllAvailableLevels(session: async_scoped_session):
    result = await session.execute(
        select(Level).filter(
            Level.awards.any()
        )
    )

    return [l.tuple()[0] for l in result.all()]


async def createAUser(session: async_scoped_session, uid: int):
    ud = User(qq_id=uid)
    session.add(ud)
    await session.flush()

    return ud


async def getOrCreateUser(session: async_scoped_session, uid: int):
    userResult = await session.execute(select(User).filter(
        User.qq_id == uid
    ))

    user = userResult.scalar_one_or_none()

    if user is None:
        user = await createAUser(session, uid)
    
    return user


def isUserHaveAward(user: User, award: Award):
    for ac in user.storage_stats:
        if ac.award == award:
            return True

    return False


async def getAwardImageOfOneUser(session: async_scoped_session | AsyncSession, user: User, award: Award) -> str:
    if session is None:
        session = get_session()

    record = (await session.execute(select(
        UsedSkin
    ).filter(
        UsedSkin.user == user
    ).filter(
        UsedSkin.skin.has(
            Skin.award == award
        )
    ))).scalar_one_or_none()

    if record == None:
        return award.img_path
    
    return record.skin.image


async def getAwardDescriptionOfOneUser(session: async_scoped_session | AsyncSession, user: User, award: Award) -> str:
    if session is None:
        session = get_session()

    record = (await session.execute(select(
        UsedSkin
    ).filter(
        UsedSkin.user == user
    ).filter(
        UsedSkin.skin.has(
            Skin.award == award
        )
    ))).scalar_one_or_none()

    if record == None or record.skin.extra_description == '':
        return award.description
    
    return record.skin.extra_description


async def getUserUsingSkin(session: async_scoped_session | AsyncSession | None, user: User, award: Award):
    if session is None:
        session = get_session()

    return (await session.execute(select(
        UsedSkin
    ).filter(
        UsedSkin.user == user
    ).filter(
        UsedSkin.skin.has(
            Skin.award == award
        )
    ))).scalar_one_or_none()


async def getGlobal(session: async_scoped_session):
    glob = (await session.execute(select(Global))).scalar_one_or_none()

    if glob is None:
        glob = Global()
        session.add(glob)
        await session.flush()
    
    return glob
