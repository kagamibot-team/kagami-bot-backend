"""
小镜！！！
"""

import asyncio
import datetime
import re

from arclet.alconna import Alconna, Arg, Arparma, MultiVar
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import GroupContext
from src.base.exceptions import (
    NotSleepTimeException,
    SleepToLateException,
    UnknownArgException,
)
from src.common.command_deco import (
    limited,
    listen_message,
    match_alconna,
    require_awake,
)
from src.common.config import get_config
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
        n = now_datetime().timestamp()
        uid = await uow.users.get_uid(ctx.sender_id)
        if await uow.users.get_getup_time(uid) > n:
            return
        arg = res.query[tuple[str]]("getup_time")
        hour, minute = parse_getup_time(arg)

        # 必须将一些逻辑放在 UOW 里面，虽然会导致一些阻塞问题，
        # 但是这种问题的耗时是微不足道的，而且可以避免出现恶性的
        # 刷薯片 Bug。
        now_time = now_datetime()
        target = now_time.replace(hour=hour, minute=minute, second=0)
        if target < now_time:
            target += datetime.timedelta(days=1)

        if hour <= now_time.hour < 21:
            raise NotSleepTimeException()

        uid = await uow.users.get_uid(ctx.sender_id)
        last_time, count = await uow.users.get_sleep_early_data(uid)
        last_dt = timestamp_to_datetime(last_time).date()
        if 21 <= now_time.hour < 23 and ((now_time.date() - last_dt).days <= 1 or get_config().safe_sleep):
            count += 1
        elif 21 <= now_time.hour < 23:
            count = 1
        else:
            count = 0
        last_time = now_time.timestamp()

        await uow.users.update_sleep_early_data(uid, last_time, count)

        awarding = 0
        if 21 <= now_time.hour < 23:
            awarding = get_random().randint(50, 100)
            await uow.chips.add(uid, awarding)

        await uow.users.set_getup_time(uid, target.timestamp())
        name = await uow.users.name(qqid=ctx.sender_id)
        await StatService(uow).sleep(uid, 21 <= now_time.hour < 23)

    # 渲染消息部分
    rep_name = ""
    if name is not None:
        rep_name = name + "！"

    await ctx.reply(
        UniMessage(f"晚安！{rep_name}")
        + get_random().choice(
            [
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
        ),
        ref=True,
        at=False,
    )

    await asyncio.sleep(get_random().random() + 0.5)
    if awarding <= 0:
        await ctx.reply(
            UniMessage("明天别睡太晚了！早睡早起身体好！").emoji(id="30").emoji(id="30")
        )
    else:
        await ctx.reply(
            UniMessage(
                f"奖励早睡的孩子 {awarding} 薯片哦，你已经坚持早睡了 {count} 天了！"
            )
        )

    await asyncio.sleep(get_random().random() + 0.5)
    await ctx.reply("我不看你的消息了哦，明天见！")
