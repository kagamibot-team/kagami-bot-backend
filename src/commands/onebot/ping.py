import asyncio
import os
import re
import time

from src.common.rd import get_random
from src.imports import *


def randomKagami():
    rootPath = os.path.join(".", "data", "kagami")

    if not os.path.exists(rootPath):
        return None

    files = os.listdir(rootPath)
    if len(files) == 0:
        return None

    return os.path.join(rootPath, get_random().choice(files))


@listenGroup()
async def ping(ctx: GroupContext):
    if (
        ctx.event.to_me
        and len(ctx.message) == 1
        and (ctx.message)[0].data["text"] == ""
    ):
        kagami = randomKagami()
        if kagami is None:
            return

        await ctx.reply(UniMessage().image(path=kagami))


@listenOnebot()
@matchRegex("^[小|柊]镜[， ,]?跳?科目三$")
@withLoading("")
async def _(ctx: PublicContext, _: Match[str]):
    await asyncio.sleep(5)


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


@listenGroup()
@matchAlconna(
    Alconna(
        "小镜晚安",
        Arg("getup_time", MultiVar(str, "*"), seps=" "),
    )
)
@requireOperatorInGroup()
@withSessionLock()
async def goodnight(ctx: GroupContext, session: AsyncSession, res: Arparma):
    info = await get_group_member_info(ctx.bot, ctx.event.group_id, ctx.sender_id)
    self_info = await get_group_member_info(
        ctx.bot, ctx.event.group_id, int(ctx.bot.self_id)
    )
    if self_info["role"] == "admin" and info["role"] != "member":
        await send_private_msg(
            ctx.bot,
            ctx.sender_id,
            UniMessage("诶……好像没办法给群里的管理员或者群主禁言……")
            .emoji(id="106")
            .emoji(id="106")
            .text("所以这个晚安没法生效了……"),
        )
        await asyncio.sleep(get_random().random() + 0.5)
        await send_private_msg(
            ctx.bot,
            ctx.sender_id,
            "所以……如果你不是管理员，你可能就能获得这个晚安的奖励了",
        )
        return

    target_hour = 8
    target_minute = 0

    arg = res.query[tuple[str]]("getup_time")

    if arg is not None and len(arg) != 0:
        arg = " ".join(arg)
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
                await ctx.reply("真能睡懒觉，要不早点起来吧", ref=True)
                return
        else:
            await ctx.reply(f"我好像没搞懂你说 {arg} 是什么意思……", ref=True)
            return

    dt = now_datetime()
    target_time: datetime.datetime | None = None
    awards: int = -1
    count: int = -1

    if dt.hour >= 21:
        target_time = (dt + datetime.timedelta(days=1)).replace(
            hour=target_hour, minute=target_minute, second=0
        )

    if dt.hour < target_hour:
        target_time = dt.replace(hour=target_hour, minute=target_minute, second=0)

    if dt.hour >= 21 and dt.hour < 23:
        uid = await get_uid_by_qqid(session, ctx.sender_id)
        query = select(User.last_sleep_early_time, User.sleep_early_count).filter(
            User.data_id == uid
        )
        last_sleep_time, sleep_count = (await session.execute(query)).tuples().one()
        last_sleep_date = timestamp_to_datetime(last_sleep_time).date()
        if (dt.date() - last_sleep_date).days < 1:
            awards = -2
        else:
            awards = get_random().randint(50, 100)
            await session.execute(
                update(User)
                .where(User.data_id == uid)
                .values(
                    last_sleep_early_time=time.time(),
                    sleep_early_count=sleep_count + 1,
                )
            )
            money = await get_user_money(session, uid)
            await set_user_money(session, uid, money + awards)
            await session.commit()
        count = sleep_count + 1

    if target_time is None:
        await ctx.reply("现在不是睡觉的时候吧……", ref=True, at=False)
        return

    delta = target_time - dt
    await set_group_ban(ctx.bot, ctx.event.group_id, ctx.sender_id, delta)

    rep_name = ""
    sender = ctx.sender_id
    custom_replies = config.custom_replies
    if (k := str(sender)) in custom_replies.keys():
        rep_name = custom_replies[k] + "！"

    await ctx.reply(
        UniMessage(f"晚安！{rep_name}")
        + get_random().choice(
            [
                "明早见哦！",
                "明早早八再见~",
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
    if awards <= 0:
        if awards == -1:
            await ctx.reply(
                UniMessage("明天别睡太晚了！早睡早起身体好！")
                .emoji(id="30")
                .emoji(id="30")
            )
        elif awards == -2:
            await ctx.reply(UniMessage("别贪心啊！今天我已经给过你薯片了！"))
    else:
        await ctx.reply(
            UniMessage(
                f"奖励早睡的孩子 {awards} 薯片哦，你已经坚持早睡了 {count} 天了！"
            )
        )
