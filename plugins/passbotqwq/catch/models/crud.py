from typing import TypeVar, Sequence
from sqlalchemy import Row, select
from nonebot_plugin_orm import async_scoped_session, get_session

from .Basics import Level, Award, AwardCountStorage, UserData


def selectAllLevelUserObtained(user: UserData):
    return select(Level).filter(
        Level.awards.any(
            Award.binded_counters.any(
                AwardCountStorage.target_user == user
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
    ud = UserData(qq_id=uid)
    session.add(ud)
    await session.commit()

    return ud


async def getOrCreateUser(session: async_scoped_session, uid: int):
    userResult = await session.execute(select(UserData).filter(
        UserData.qq_id == uid
    ))

    user = userResult.scalar_one_or_none()

    if user is None:
        user = await createAUser(session, uid)
    
    return user


def isUserHaveAward(user: UserData, award: Award):
    for ac in user.award_counters:
        if ac.target_award == award:
            return True

    return False
