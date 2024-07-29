import random
import time

import PIL.Image
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import GroupContext
from src.base.local_storage import LocalStorageManager
from src.base.onebot.onebot_enum import QQEmoji
from src.common.data.awards import get_award_info
from src.common.decorators.command_decorators import listenGroup, matchRegex
from src.common.rd import get_random
from src.common.times import now_datetime, timestamp_to_datetime, to_utc8
from src.core.unit_of_work import get_unit_of_work
from src.logic.daily import get_daily
from src.ui.base.basics import Fonts, render_text, vertical_pile
from src.ui.base.tools import image_to_bytes
from src.ui.components.catch import catch
from src.ui.views.award import AwardDisplay


@listenGroup()
@matchRegex("^(小镜|xj)(今日人品|jrrp)$")
async def _(ctx: GroupContext, _):
    qqid = ctx.sender_id
    dt = now_datetime()

    if qqid is None:
        qqid = 0

    today_user: random.Random = random.Random(str(qqid) + "-" + str(dt.date()))
    jrrp = today_user.randint(1, 100)

    async with get_unit_of_work(qqid) as uow:
        aid = await get_daily(uow)
        info = await get_award_info(uow, aid)
        name = await ctx.get_sender_name()

    titles: list[PIL.Image.Image] = []
    titles.append(
        render_text(
            text=(f"玩家 {name} ："),
            color="#9B9690",
            font=Fonts.ALIMAMA_SHU_HEI,
            font_size=48,
        )
    )
    titles.append(
        render_text(
            text=f"您的今日人品是： {str(jrrp)}！",
            color="#63605C",
            font=Fonts.JINGNAN_BOBO_HEI,
            font_size=80,
        )
    )
    titles.append(
        render_text(
            text="本次今日小哥是：",
            color="#63605C",
            font=Fonts.JINGNAN_BOBO_HEI,
            font_size=80,
        )
    )

    area_box = catch(AwardDisplay(info=info))

    area_title = vertical_pile(titles, 0, "left", "#EEEBE3", 0, 0, 0, 0)
    img = vertical_pile([area_title, area_box], 30, "left", "#EEEBE3", 60, 80, 80, 80)
    await ctx.send(UniMessage().image(raw=image_to_bytes(img)))

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
async def _(ctx: GroupContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        ts, count = await uow.users.get_sign_in_info(uid)

        last_sign_date = to_utc8(timestamp_to_datetime(ts)).date()
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

        await uow.users.add_money(uid, moneydelta)
        await uow.users.set_sign_in_info(uid, time.time(), count)

    await ctx.reply(f"签到成功！你已经连续签到 {count} 天了，得到了 {moneydelta} 薯片")
    no = LocalStorageManager.instance().data.sign(ctx.event.group_id)
    LocalStorageManager.instance().save()
    if no == 1:
        await ctx.stickEmoji(QQEmoji.NO)
    elif no == 2:
        await ctx.stickEmoji(QQEmoji.胜利)
    elif no == 3:
        await ctx.stickEmoji(QQEmoji.OK)
