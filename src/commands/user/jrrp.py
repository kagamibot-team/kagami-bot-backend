import time

from src.base.command_events import GroupContext
from src.base.localdata import LocalStorageManager
from src.base.onebot.onebot_enum import QQEmoji
from src.common.command_deco import limited, listen_message, match_regex, require_awake
from src.common.rd import get_random
from src.common.times import now_datetime, timestamp_to_datetime, to_utc8
from src.core.unit_of_work import get_unit_of_work
from src.services.stats import StatService


@listen_message()
@limited
@match_regex("^(小镜|xj)(签到|qd)$")
@require_awake
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

        await uow.money.add(uid, moneydelta)
        await uow.users.set_sign_in_info(uid, time.time(), count)
        await StatService(uow).sign(uid)

    await ctx.reply(
        f"签到成功！你已经连续签到 {count} 天了。\n您的今日人品是 {moneydelta} ，获得了对应量的薯片！"
    )
    no = LocalStorageManager.instance().data.sign(ctx.event.group_id)
    LocalStorageManager.instance().save()
    if no == 1:
        await ctx.stickEmoji(QQEmoji.NO)
    elif no == 2:
        await ctx.stickEmoji(QQEmoji.胜利)
    elif no == 3:
        await ctx.stickEmoji(QQEmoji.OK)

    if moneydelta == 100:
        await ctx.stickEmoji(QQEmoji.比心)
    elif moneydelta >= 90:
        await ctx.stickEmoji(QQEmoji.庆祝)
    elif moneydelta >= 80:
        await ctx.stickEmoji(QQEmoji.赞)
    elif moneydelta >= 60:
        await ctx.stickEmoji(QQEmoji.棒棒糖)
    elif moneydelta >= 40:
        await ctx.stickEmoji(QQEmoji.托腮)
    elif moneydelta >= 20:
        await ctx.stickEmoji(QQEmoji.糗大了)
    elif moneydelta >= 10:
        await ctx.stickEmoji(QQEmoji.笑哭)
    elif moneydelta > 1:
        await ctx.stickEmoji(QQEmoji.泪奔)
    else:
        await ctx.stickEmoji(QQEmoji.Emoji猴)
