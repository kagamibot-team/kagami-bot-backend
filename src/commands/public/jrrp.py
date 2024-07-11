import random
import time

from src.base.local_storage import LocalStorageManager
from src.common.rd import get_random
from src.imports import *


@listenGroup()
@matchRegex("^(小镜|xj)(今日人品|jrrp)$")
@withSessionLock()
async def _(ctx: GroupContext, session: AsyncSession, _):
    qqid = ctx.getSenderId()
    dt = now_datetime()

    if qqid is None:
        qqid = 0

    today_user: random.Random = random.Random(str(qqid) + "-" + str(dt.date()))
    today: random.Random = random.Random(str(dt.date()))

    jrrp = today_user.randint(1, 100)

    level = today.choices(level_repo.sorted, [l.weight for l in level_repo.sorted])[0]
    query = select(Award.data_id).filter(Award.level_id == level.id)
    awards = (await session.execute(query)).tuples().all()
    aid = today.choice(awards)[0]
    display = await get_award_info(session, -1, aid)

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderName()

    titles: list[PIL.Image.Image] = []
    titles.append(
        await getTextImage(
            text=(f"玩家 {name} ："),
            color="#9B9690",
            font=Fonts.ALIMAMA_SHU_HEI,
            font_size=48,
        )
    )
    titles.append(
        await getTextImage(
            text=f"您的今日人品是： {str(jrrp)}！",
            color="#63605C",
            font=Fonts.JINGNAN_BOBO_HEI,
            font_size=80,
        )
    )
    titles.append(
        await getTextImage(
            text="本次今日小哥是：",
            color="#63605C",
            font=Fonts.JINGNAN_BOBO_HEI,
            font_size=80,
        )
    )

    area_box = await catch(
        title=display.awardName,
        description=display.awardDescription,
        image=display.awardImg,
        stars=display.levelName,
        color=display.color,
        new=False,
        notation="",
    )

    area_title = await verticalPile(titles, 0, "left", "#EEEBE3", 0, 0, 0, 0)
    img = await verticalPile(
        [area_title, area_box], 30, "left", "#EEEBE3", 60, 80, 80, 80
    )
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))
    # await ctx.reply(UniMessage().text(f"你的今日人品是：{str(jrrp)}。\n本次今日小哥是：{diplay.awardName}。"))

    if isinstance(ctx, GroupContext):
        if jrrp == 100:
            await ctx.stickEmoji(QQEmoji.比心)
        elif jrrp >= 90:
            await ctx.stickEmoji(QQEmoji.庆祝)
        elif jrrp >= 80:
            await ctx.stickEmoji(QQEmoji.赞)
        elif jrrp >= 60:
            await ctx.stickEmoji(QQEmoji.棒棒糖)
        elif jrrp >= 40:
            await ctx.stickEmoji(QQEmoji.托腮)
        elif jrrp >= 20:
            await ctx.stickEmoji(QQEmoji.糗大了)
        elif jrrp >= 10:
            await ctx.stickEmoji(QQEmoji.笑哭)
        elif jrrp > 1:
            await ctx.stickEmoji(QQEmoji.泪奔)
        else:
            await ctx.stickEmoji(QQEmoji.Emoji猴)


@listenGroup()
@matchRegex("^(小镜|xj)(签到|qd)$")
@withSessionLock()
async def _(ctx: GroupContext, session: AsyncSession, _):
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

    moneydelta = (1 - get_random().random() ** ((count - 1) * 0.2 + 1)) * 90 + 10
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

    no = LocalStorageManager.instance().data.sign(ctx.event.group_id)
    LocalStorageManager.instance().save()
    if no == 1:
        await ctx.stickEmoji(QQEmoji.NO)
    elif no == 2:
        await ctx.stickEmoji(QQEmoji.胜利)
    elif no == 3:
        await ctx.stickEmoji(QQEmoji.OK)
