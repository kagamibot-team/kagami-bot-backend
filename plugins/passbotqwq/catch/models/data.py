from nonebot_plugin_orm import async_scoped_session
from sqlalchemy import select, update

from .crud import getAllLevels
from .Basics import Award, AwardCountStorage, Level, UserData


async def setEveryoneInterval(session: async_scoped_session, interval: float):
    await session.execute(update(UserData).values(pick_time_delta=interval))


async def addAward(session: async_scoped_session, user: UserData, award: Award, delta: int):
    aws = (await session.execute(select(AwardCountStorage).filter(
        AwardCountStorage.target_award == award
    ).filter(
        AwardCountStorage.target_user == user
    ))).scalar_one_or_none()

    if aws is None:
        aws = AwardCountStorage(
            target_user=user,
            target_award=award,
            award_count=0,
        )
        session.add(aws)

    aws.award_count += delta

    return aws.award_count


async def getPosibilities(session: async_scoped_session, level: Level):
    levels = await getAllLevels(session)
    weightSum = sum([l.weight for l in levels])

    return level.weight / weightSum
