import time
from src.common.fast_import import *


async def getInterval(session: AsyncSession):
    dt = (await session.execute(select(Global.catch_interval))).scalar_one_or_none()

    if dt is None:
        config = Global()
        session.add(config)
        await session.flush()

        return 3600
    return dt


async def updateUserTime(
    session: AsyncSession, uid: int, count_remain: int, last_calc: float
):
    """
    更新玩家抓小哥的时间
    """

    await session.execute(
        update(User)
        .where(User.data_id == uid)
        .values(pick_count_remain=count_remain, pick_count_last_calculated=last_calc)
    )


async def calculateTime(session: AsyncSession, uid: int):
    """
    根据当前时间，重新计算玩家抓小哥的时间和上限。
    该函数会自动更新数据库中的数据。
    """

    maxPickCount, pick_count_remain, pick_count_last_calculated = (
        (
            await session.execute(
                select(
                    User.pick_max_cache,
                    User.pick_count_remain,
                    User.pick_count_last_calculated,
                ).where(User.data_id == uid)
            )
        )
        .one()
        .tuple()
    )
    pickInterval = await getInterval(session)
    now = time.time()

    if pickInterval == 0:
        await updateUserTime(session, uid, maxPickCount, now)
        return maxPickCount, now, maxPickCount

    if pick_count_remain >= maxPickCount:
        await updateUserTime(session, uid, pick_count_remain, now)
        return pick_count_remain, now, maxPickCount

    cycles = int((now - pick_count_last_calculated) / pickInterval)
    pick_count_last_calculated += cycles * pickInterval
    pick_count_remain += cycles

    if pick_count_remain > maxPickCount:
        pick_count_remain = maxPickCount
        pick_count_last_calculated = now

    await updateUserTime(session, uid, pick_count_remain, pick_count_last_calculated)

    return pick_count_remain, pick_count_last_calculated, maxPickCount


async def timeToNextCatch(session: AsyncSession, user: User):
    """
    计算玩家下一次抓小哥的时间，在调用这个方法前，请先调用 `calculateTime`。
    """

    maxPickCount = user.pick_max_cache
    pickInterval = await getInterval(session)

    now = time.time()

    if pickInterval == 0:
        return now

    if user.pick_count_remain >= maxPickCount:
        return now

    return user.pick_count_last_calculated + pickInterval
