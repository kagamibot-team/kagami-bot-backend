from src.common.dataclasses.user import UserTime
from src.common.times import now_datetime
from src.core.unit_of_work import UnitOfWork


def recalculate_time_logic(data: UserTime, now: float | None = None) -> UserTime:
    # 这里把时间分出来了，为了方便做单元测试
    if now is None:
        now_t = now_datetime().timestamp()
    else:
        now_t = now

    time_delta = now_t - data.last_updated_timestamp

    if time_delta <= data.interval:
        return data

    if data.interval <= 0:
        # 测试环境中，你们很喜欢把周期调成 0，嗯
        data.slot_empty = data.slot_count
    else:
        collected = int(time_delta / data.interval)
        data.slot_empty += collected

        if data.slot_empty >= data.slot_count:
            # 收集满了
            data.slot_empty = data.slot_count
            data.last_updated_timestamp = now_t
        else:
            data.last_updated_timestamp += data.interval * collected

    return data


async def uow_calculate_time(uow: UnitOfWork, uid: int) -> UserTime:
    """根据当前时间，重新计算玩家抓小哥的时间和上限，并更新数据库中的数据。

    Args:
        uow (UnitOfWork): 工作单元
        uid (int): 用户 ID

    Returns:
        UserTime: 玩家抓小哥的时间和上限信息
    """

    data = await uow.user_catch_time.get_user_time(uid)
    data = recalculate_time_logic(
        UserTime(
            slot_count=data.slot_count,
            slot_empty=data.slot_empty,
            last_updated_timestamp=data.last_updated_timestamp,
            interval=await uow.settings.get_interval(),
        )
    )
    await uow.user_catch_time.set_user_time(uid, data)
    return data
