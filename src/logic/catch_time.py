import time
from src.imports import *


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
    """更新玩家抓小哥的时间

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户在数据库中的 ID
        count_remain (int): 剩余抓的次数
        last_calc (float): 上一次计算抓的时间
    """

    await session.execute(
        update(User)
        .where(User.data_id == uid)
        .values(pick_count_remain=count_remain, pick_count_last_calculated=last_calc)
    )


async def calculateTime(session: AsyncSession, uid: int) -> UserTime:
    """
    根据当前时间，重新计算玩家抓小哥的时间和上限。
    该函数不会更新数据库中的数据。

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户在数据库中的 ID
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
        .tuples()
        .one()
    )
    pickInterval = await getInterval(session)
    now = time.time()

    if pickInterval == 0:
        pick_count_remain = max(maxPickCount, pick_count_remain)
        pick_count_last_calculated = now
    elif pick_count_remain >= maxPickCount:
        pick_count_last_calculated = now
    else:
        cycles = int((now - pick_count_last_calculated) / pickInterval)
        pick_count_last_calculated += cycles * pickInterval
        pick_count_remain += cycles

        if pick_count_remain > maxPickCount:
            pick_count_remain = maxPickCount
            pick_count_last_calculated = now

    return UserTime(
        pickMax=maxPickCount,
        pickRemain=pick_count_remain,
        pickLastUpdated=pick_count_last_calculated,
        interval=pickInterval,
    )


async def uow_calculate_time(uow: UnitOfWork, uid: int) -> UserTime:
    """*重构需要* 根据当前时间，重新计算玩家抓小哥的时间和上限，并更新数据库中的数据。

    Args:
        uow (UnitOfWork): 工作单元
        uid (int): 用户 ID

    Returns:
        UserTime: 玩家抓小哥的时间和上限信息
    """
    return await calculateTime(uow.session, uid)
