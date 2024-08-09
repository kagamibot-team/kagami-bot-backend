import re
import time

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma
from nonebot_plugin_alconna import At, Reply, Text

from src.base.command_events import OnebotContext
from src.base.event.event_root import throw_event
from src.base.exceptions import KagamiRangeError
from src.base.local_storage import Action, LocalStorageManager, XBRecord
from src.common.data.awards import get_award_info
from src.common.dataclasses.game_events import UserTryCatchEvent
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    matchRegex,
)
from src.common.times import now_datetime
from src.core.unit_of_work import get_unit_of_work
from src.logic.catch import pickAwards
from src.logic.catch_time import uow_calculate_time
from src.ui.pages.catch import render_catch_message
from src.ui.views.award import GotAwardDisplay
from src.ui.views.catch import CatchMesssage, CatchResultMessage
from src.ui.views.user import UserData


async def picks(
    qqid: int,
    qqname: str | None = None,
    count: int | None = None,
    group_id: int | None = None,
) -> CatchMesssage:
    """在一次数据库操作中抓小哥。流程如下：
    - 刷新计算用户的时间，包括抓小哥的时间和可以抓的次数
    - 抓一次小哥，先把结果存在内存中
    - 发布 `PicksEvent` 事件以允许对结果进行修改
    - 将数据写入数据库会话中

    Args:
        ctx (OnebotContext): 上下文
        uow (UnitOfWork): 工作单元
        uid (int): 用户id
        count (int | None, optional): 抓取次数. Defaults to None.
        group_id (int | None, optional): 群号，用于记录喜报. Defaults to None.
    Returns:
        CatchMesssage: 抓取结果
    """

    if qqname is None:
        qqname = str(qqid)

    async with get_unit_of_work(qqid) as uow:
        uid = await uow.users.get_uid(qqid)
        user_time = await uow_calculate_time(uow, uid)

        if count is None:
            count = user_time.pickRemain

        if count <= 0 and user_time.pickRemain != 0:
            raise KagamiRangeError("抓小哥次数", "大于 0 的数", count)

        count = min(user_time.pickRemain, count)
        count = max(0, count)

        pick_result = await pickAwards(uow, uid, count)
        spent_count = 0
        catchs: list[GotAwardDisplay] = []

        for aid, pick in pick_result.awards.items():
            spent_count += pick.delta
            await uow.inventories.give(uid, aid, pick.delta)
            info = await get_award_info(uow, aid, uid)
            info = GotAwardDisplay(
                info=info, count=pick.delta, is_new=pick.beforeStats == 0
            )
            catchs.append(info)

        await uow.users.update_catch_time(
            uid,
            user_time.pickRemain - spent_count,
            user_time.pickLastUpdated,
        )
        await uow.money.add(uid, pick_result.money)
        user = UserData(
            uid=uid,
            qqid=str(qqid),
            name=qqname,
        )

        if spent_count > 0:
            msg = CatchResultMessage(
                user=user,
                slot_remain=user_time.pickRemain - spent_count,
                slot_sum=user_time.pickMax,
                next_time=user_time.pickLastUpdated + user_time.interval - time.time(),
                money_changed=int(pick_result.money),
                money_sum=int(await uow.money.get(uid)),
                catchs=catchs,
                group_id=group_id,
            )
        else:
            msg = CatchMesssage(
                user=user,
                slot_remain=user_time.pickRemain - spent_count,
                slot_sum=user_time.pickMax,
                next_time=user_time.pickLastUpdated + user_time.interval - time.time(),
                group_id=group_id,
            )

    await handle_xb(msg)
    await throw_event(UserTryCatchEvent(user_data=user, catch_view=msg))
    return msg


async def handle_xb(msg: CatchMesssage):
    if not isinstance(msg, CatchResultMessage):
        return

    if msg.group_id is None:
        return

    data: list[str] = []
    for info in msg.catchs:
        if info.info.level.lid not in (4, 5):
            continue

        new_hint = "（新）" if info.new else ""
        data.append(f"{info.info.name} ×{info.notation[1:]}{new_hint}")

    if len(data) > 0:
        LocalStorageManager.instance().data.add_xb(
            msg.group_id,
            msg.user.qqid,
            XBRecord(time=now_datetime(), action=Action.catched, data="，".join(data)),
        )
        LocalStorageManager.instance().save()


@listenOnebot()
@matchAlconna(
    Alconna("re:(抓小哥|zhua|抓抓)", Arg("count", int, flags=[ArgFlag.OPTIONAL]))
)
async def _(ctx: OnebotContext, result: Arparma):
    count = result.query[int]("count")
    if count is None:
        count = 1
    msg = await picks(
        ctx.sender_id,
        await ctx.sender_name,
        count,
        group_id=ctx.group_id,
    )
    await ctx.send(await render_catch_message(msg))


@listenOnebot()
@matchRegex("^(狂抓|kz|狂抓小哥|kZ|Kz|KZ)$")
async def _(ctx: OnebotContext, _):
    msg = await picks(
        ctx.sender_id,
        await ctx.sender_name,
        group_id=ctx.group_id,
    )
    await ctx.send(await render_catch_message(msg))


@listenOnebot()
async def _(ctx: OnebotContext):
    msg = ctx.message.exclude(At).exclude(Reply)
    if not msg.only(Text):
        return
    msg = msg.extract_plain_text().strip()
    if not re.match("^是[。.！!？? ]*$", msg):
        return
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        flags_before = await uow.user_flag.get(uid)
        await uow.user_flag.add(uid, "是")
        utime = await uow_calculate_time(uow, uid)
    if utime.pickRemain > 0:
        msg = await picks(
            ctx.sender_id,
            await ctx.sender_name,
            1,
            group_id=ctx.group_id,
        )
        await ctx.send(await render_catch_message(msg))
    elif "是" not in flags_before:
        await ctx.reply("收到。", ref=True)
    else:
        await ctx.reply("是", ref=True, at=False)
