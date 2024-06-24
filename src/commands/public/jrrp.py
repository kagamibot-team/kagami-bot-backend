import random
import time

from src.common.dataclasses.sign_in_history import signInHistor
from src.imports import *


@listenPublic()
@matchLiteral("小镜jrrp")
async def _(ctx: PublicContext):
    qqid = ctx.getSenderId()
    dt = now_datetime()

    if qqid is None:
        qqid = 0

    random.seed(str(qqid) + "-" + str(dt.date()))
    jrrp = random.randint(1, 100)

    await ctx.reply(UniMessage().text("你的今日人品是：" + str(jrrp)))

    if isinstance(ctx, GroupContext):
        if jrrp == 100:
            await ctx.stickEmoji(QQEmoji.比心)
        elif jrrp >= 90:
            await ctx.stickEmoji(QQEmoji.庆祝)
        elif jrrp >= 80:
            await ctx.stickEmoji(QQEmoji.赞)
        elif jrrp >= 60:
            await ctx.stickEmoji(QQEmoji.OK)
        elif jrrp >= 40:
            await ctx.stickEmoji(QQEmoji.托腮)
        elif jrrp >= 20:
            await ctx.stickEmoji(QQEmoji.辣眼睛)
        elif jrrp >= 10:
            await ctx.stickEmoji(QQEmoji.笑哭)
        elif jrrp > 1:
            await ctx.stickEmoji(QQEmoji.泪奔)
        else:
            await ctx.stickEmoji(QQEmoji.Emoji猴)


@listenGroup()
@matchLiteral("签到")
@withSessionLock()
async def _(ctx: GroupContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    query = select(User.last_sign_in_time, User.sign_in_count, User.money).filter(
        User.data_id == uid
    )

    last_sign_in, count, money = (await session.execute(query)).tuples().one()

    last_sign_date = to_utc8(timestamp_to_datetime(last_sign_in)).date()
    now_date = now_datetime().date()

    moneydelta = 0

    if (now_date - last_sign_date).days == 0:
        await ctx.reply("你今天已经签到过了哦～")
        return

    if (now_date - last_sign_date).days > 1:
        count = 1
    else:
        count += 1

    moneydelta = (1 - random.random() ** ((count - 1) * 0.2 + 1)) * 90 + 10
    moneydelta = int(moneydelta)

    await session.execute(
        update(User)
        .filter(User.data_id == uid)
        .values(
            sign_in_count=count, last_sign_in_time=time.time(), money=money + moneydelta
        )
    )

    await session.commit()
    await ctx.reply(f"签到成功！你已经连续签到 {count} 天了，得到了 {moneydelta} 薯片")

    no = signInHistor.sign(ctx.event.group_id)
    if no == 1:
        await ctx.stickEmoji(QQEmoji.NO)
    elif no == 2:
        await ctx.stickEmoji(QQEmoji.胜利)
    elif no == 3:
        await ctx.stickEmoji(QQEmoji.OK)
