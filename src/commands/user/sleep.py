"""
小镜！！！
"""

import asyncio
import datetime
import re
from typing import Any

from arclet.alconna import Alconna, Arg, Arparma, MultiVar
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import GroupContext
from src.base.exceptions import (
    NotSleepTimeException,
    SleepToLateException,
    UnknownArgException,
)
from src.common.command_deco import limited, listen_message, match_alconna
from src.common.config import Config, get_config
from src.common.rd import get_random
from src.common.times import now_datetime, timestamp_to_datetime
from src.core.unit_of_work import get_unit_of_work
from src.services.stats import StatService

GET_UP_TIME_PRESETS = {
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
    "十一": 11,
    "十二": 12,
}


def parse_getup_time(inp: tuple[str] | None) -> tuple[int, int]:
    """根据输入的值来分析睡觉的时间

    Args:
        inp (tuple[str] | None): 输入的值，可能不存在

    Returns:
        tuple[int, int]: 睡觉的小时与分钟
    """
    target_hour = 8
    target_minute = 0

    if inp is not None and len(inp) != 0:
        arg = " ".join(inp)
        if match := re.match(
            (
                "^(明天?|明儿?)?"
                "(大?早上?)?[，, ]?"
                "(我?想?要?) ?"
                "(四|五|六|七|八|九|十|十一|十二|4|5|6|7|8|9|10|11|12) ?点(半)?钟?"
                "再?(起床?来?|醒来?)?$"
            ),
            arg,
        ):
            ma = match.group(4)
            if ma.isdigit():
                target_hour = int(ma)
            elif ta := GET_UP_TIME_PRESETS.get(ma):
                target_hour = ta
            else:
                target_hour = 8

            ma2 = match.group(5)
            if ma2 is not None:
                target_minute = 30

            if target_hour > 10:
                raise SleepToLateException()
        else:
            raise UnknownArgException(arg)

    return target_hour, target_minute


@listen_message()
@limited
@match_alconna(
    Alconna(
        "小镜晚安",
        Arg("getup_time", MultiVar(str, "*"), seps=" "),
    )
)
async def goodnight(ctx: GroupContext, res: Arparma):
    async with get_unit_of_work(ctx.sender_id) as uow:
        now_time = now_datetime()
        now_timestamp = now_time.timestamp()
        uid = await uow.users.get_uid(ctx.sender_id)

        if await uow.users.get_getup_time(uid) > now_timestamp:
            # 如果起床时间比当前时间晚，说明玩家已经晚安了
            # 这时候应该忽略这个命令
            return

        # 获取玩家期望的起床时间
        arg = res.query[tuple[str]]("getup_time")
        hour, minute = parse_getup_time(arg)

        # 计算玩家期望的起床时间
        target = now_time.replace(hour=hour, minute=minute, second=0)
        if target < now_time:
            # 大概率这个时间是今天的早上，所以需要加一天
            target += datetime.timedelta(days=1)

        if hour <= now_time.hour < 21:
            # 现在还不是睡觉时间，不能睡觉
            raise NotSleepTimeException()

        # 更新玩家的起床时间和连胜计数
        last_time, count = await uow.users.get_sleep_early_data(uid)
        success = is_sleep_early(now_time)
        last_time, count = update_sleep_data(now_time, last_time, count, success)

        # 计算奖励
        awarding = get_random().randint(50, 100) if success else 0

        # 保存数据
        await uow.users.update_sleep_early_data(uid, last_time, count)
        await uow.users.set_getup_time(uid, target.timestamp())
        await StatService(uow).sleep(uid, success)
        await uow.chips.add(uid, awarding)

        name = await uow.users.name(qqid=ctx.sender_id)

    await reply_messages(ctx, name, awarding, count)


def update_sleep_data(
    now_time: datetime.datetime,
    last_time: float,
    count: int,
    success: bool,
) -> tuple[float, int]:
    """
    根据当前时间和上次早睡时间更新早睡计数。

    参数:
        now_time (datetime.datetime): 当前时间。
        last_dt (datetime.date): 上次早睡的日期。
        count (int): 当前的早睡计数。
        success (bool): 是否早睡成功。

    返回:
        int: 更新后的早睡计数。
    """
    if (
        success
        and (now_time.date() - timestamp_to_datetime(last_time).date()).days <= 1
    ):
        count += 1
    elif success:
        count = 1
    else:
        count = 0
    return now_time.timestamp(), count


def is_sleep_early(now_time: datetime.datetime, config: Config | None = None):
    """
    判断当前睡觉时间是否胜利。

    参数:
        now_time (datetime.datetime): 当前时间。
    """
    config = config or get_config()
    return 21 <= now_time.hour < 23 or config.safe_sleep


GOODNIGHT_MESSAGES: list[str | UniMessage[Any]] = [
    "明早见哦！",
    "睡个好觉哦！",
    "呼呼——",
    "zzz……",
    "放下手机睡觉吧！",
    "做个好梦！",
    "明天见！",
    UniMessage().emoji(id="202").emoji(id="202").emoji(id="202"),
    UniMessage().emoji(id="75").emoji(id="75"),
    UniMessage().emoji(id="8"),
]

SLEEP_LATE_MESSAGE = (
    UniMessage("明天别睡太晚了！早睡早起身体好！").emoji(id="30").emoji(id="30")
)


async def reply_messages(
    ctx: GroupContext,
    name: str | None,
    awarding: int,
    count: int,
) -> None:
    rep_name = ""
    if name is not None:
        rep_name = name + "！"

    await ctx.reply(
        UniMessage(f"晚安！{rep_name}") + get_random().choice(GOODNIGHT_MESSAGES),
        ref=True,
        at=False,
    )

    await asyncio.sleep(get_random().random() + 0.5)
    if awarding <= 0:
        await ctx.reply(SLEEP_LATE_MESSAGE)
    else:
        await ctx.reply(
            f"奖励早睡的孩子 {awarding} 薯片哦，你已经坚持早睡了 {count} 天了！"
        )

    await ctx.reply("我不看你的消息了哦，明天见！")
