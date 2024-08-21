import re
import time

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma
from nonebot_plugin_alconna import At, Reply, Text

from src.base.command_events import GroupContext
from src.base.event.event_root import throw_event
from src.base.exceptions import KagamiRangeError
from src.common.command_decorators import (
    listen_message,
    match_alconna,
    match_regex,
    require_awake,
)
from src.common.data.awards import get_award_info
from src.common.data.user import get_user_data
from src.common.dataclasses.game_events import UserTryCatchEvent
from src.core.unit_of_work import UnitOfWork, get_unit_of_work
from src.logic.catch import pickAwards
from src.logic.catch_time import uow_calculate_time
from src.ui.pages.catch import render_catch_message
from src.ui.types.common import UserData
from src.ui.types.zhua import GetAward, ZhuaData, ZhuaMeta


def timedelta_text(seconds: float):
    result = ""
    hours = int(seconds / 3600)
    minutes = int(seconds / 60) % 60
    seconds = int(seconds) % 60
    if hours > 0:
        result += f"{hours}小时"
    if hours > 0 or minutes > 0:
        result += f"{minutes}分钟"
    result += f"{seconds}秒"
    return result


async def picks(
    uow: UnitOfWork,
    user: UserData,
    count: int | None = None,
    group_id: int | None = None,
):
    """在一次数据库操作中抓小哥。流程如下：
    - 刷新计算用户的时间，包括抓小哥的时间和可以抓的次数
    - 抓一次小哥，先把结果存在内存中
    - 发布 `PicksEvent` 事件以允许对结果进行修改
    - 将数据写入数据库会话中

    Args:
        ctx (GroupContext): 上下文
        uow (UnitOfWork): 工作单元
        uid (int): 用户id
        count (int | None, optional): 抓取次数. Defaults to None.
        group_id (int | None, optional): 群号，用于记录喜报. Defaults to None.
    Returns:
        CatchMesssage: 抓取结果
    """

    uid = user.uid
    user_time = await uow_calculate_time(uow, uid)

    if count is None:
        count = user_time.pickRemain

    if count <= 0 and user_time.pickRemain != 0:
        raise KagamiRangeError("抓小哥次数", "大于 0 的数", count)

    count = min(user_time.pickRemain, count)
    count = max(0, count)

    pick_result = await pickAwards(uow, uid, count)
    spent_count = 0
    catchs: list[GetAward] = []

    for aid, pick in pick_result.awards.items():
        spent_count += pick.delta
        await uow.inventories.give(uid, aid, pick.delta)
        catchs.append(
            GetAward(
                info=await get_award_info(uow, aid, uid),
                count=pick.delta,
                is_new=pick.beforeStats == 0,
            )
        )

    await uow.users.update_catch_time(
        uid,
        user_time.pickRemain - spent_count,
        user_time.pickLastUpdated,
    )
    await uow.money.add(uid, pick_result.money)
    pack_id = await uow.user_pack.get_using(uid)

    msg = ZhuaData(
        user=user,
        meta=ZhuaMeta(
            field_from=pack_id,
            get_chip=int(pick_result.money),
            own_chip=int(await uow.money.get(uid)),
            remain_time=user_time.pickRemain - spent_count,
            max_time=user_time.pickMax,
            need_time=timedelta_text(
                user_time.pickLastUpdated + user_time.interval - time.time()
            ),
        ),
        catchs=catchs,
    )
    await throw_event(UserTryCatchEvent(user_data=user, data=msg))
    return msg


@listen_message()
@match_alconna(
    Alconna("re:(抓小哥|zhua|抓抓)", Arg("count", int, flags=[ArgFlag.OPTIONAL]))
)
@require_awake
async def _(ctx: GroupContext, result: Arparma):
    count = result.query[int]("count")
    if count is None:
        count = 1
    async with get_unit_of_work(ctx.sender_id) as uow:
        msg = await picks(
            uow,
            await get_user_data(ctx, uow),
            count,
            group_id=ctx.group_id,
        )
    await ctx.send(await render_catch_message(msg))


@listen_message()
@match_regex("^(狂抓|kz|狂抓小哥|kZ|Kz|KZ)$")
@require_awake
async def _(ctx: GroupContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        msg = await picks(
            uow,
            await get_user_data(ctx, uow),
            group_id=ctx.group_id,
        )
    await ctx.send(await render_catch_message(msg))


@listen_message()
async def _(ctx: GroupContext):
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
        async with get_unit_of_work(ctx.sender_id) as uow:
            msg = await picks(
                uow,
                await get_user_data(ctx, uow),
                1,
                group_id=ctx.group_id,
            )
        await ctx.send(await render_catch_message(msg))
    elif "是" not in flags_before:
        await ctx.reply("收到。", ref=True)
    else:
        await ctx.reply("是", ref=True, at=False)
