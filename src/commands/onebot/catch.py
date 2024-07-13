import time

from interfaces.nonebot.views.catch import render_catch_failed_message, render_catch_result_message
from src.imports import *
from src.logic.catch import pickAwards
from src.logic.catch_time import calculateTime, updateUserTime
from src.views.catch import CatchMesssage, CatchResultMessage


async def sendPickMessage(ctx: OnebotMessageContext, e: PrePickMessageEvent):
    catchs: list[AwardInfo] = []

    async with UnitOfWork(DatabaseManager.get_single()) as uow:
        for aid, display in e.displays.items():
            aifo = await uow_get_award_info(uow, aid, e.uid)
            aifo.new = display.pick.beforeStats == 0
            aifo.notation = f"+{display.pick.delta}"
            catchs.append(aifo)

    message = CatchResultMessage(
        username=await ctx.getSenderName(),
        money_changed=int(e.picks.money),
        money_sum=int(e.moneyUpdated),
        slot_remain=e.userTime.pickRemain,
        slot_sum=e.userTime.pickMax,
        next_time=e.userTime.pickLastUpdated + e.userTime.interval - time.time(),
        catchs=catchs,
    )
    await ctx.send(await render_catch_result_message(message))


async def save_picks(
    *,
    pickResult: Picks,
    group_id: int | None,
    uid: int,
    session: AsyncSession,
    userTime: UserTime,
):
    preEvent = PrePickMessageEvent(pickResult, group_id, {}, uid, session, userTime)

    # 在这里进行了数据库库存的操作
    spent_count = 0

    for aid in pickResult.awards.keys():
        pick = pickResult.awards[aid]
        spent_count += pick.delta
        
        now_stats = await get_statistics(session, uid, aid)
        await give_award(session, uid, aid, pick.delta)

        query = (
            select(
                Award.name,
                Award.image,
                Award.description,
                Award.level_id,
            )
            .filter(Award.data_id == aid)
        )
        name, image, description, lid = (
            (await session.execute(query)).tuples().one()
        )

        level = level_repo.levels[lid]

        preEvent.displays[aid] = PickDisplay(
            name=name,
            image=image,
            description=description,
            level=level.display_name,
            color=level.color,
            beforeStorage=now_stats,
            pick=pick,
        )

    await updateUserTime(
        session=session,
        uid=uid,
        count_remain=userTime.pickRemain - spent_count,
        last_calc=userTime.pickLastUpdated,
    )
    preEvent.userTime.pickRemain = userTime.pickRemain - spent_count
    query = (
        update(User)
        .where(User.data_id == uid)
        .values(money=User.money + pickResult.money)
        .returning(User.money)
    )
    res = (await session.execute(query)).scalar_one()
    preEvent.moneyUpdated = res

    return preEvent


async def picks(
    ctx: OnebotMessageContext, session: AsyncSession, uid: int, count: int | None = None
):
    """
    进行一次抓小哥。抓小哥的流程如下：
    - 刷新计算用户的时间，包括抓小哥的时间和可以抓的次数
    - 抓一次小哥，先把结果存在内存中
    - 发布 `PicksEvent` 事件以允许对结果进行修改
    - 将数据写入数据库会话中
    - 发布 `PrePickMessageEvent` 事件以方便为消息展示做准备
    - 数据库提交更改并关闭
    - 生成图片，发送回复

    Args:
        ctx (OnebotMessageContext): 抓小哥的上下文
        session (AsyncSession): 所开启的数据库会话，将会在中途关闭
        uid (int): 数据库中的用户 ID
        count (int | None, optional): 抓的次数，如果为 None，则尽可能多抓
    """

    userTime = await calculateTime(session, uid)

    if count is None:
        count = userTime.pickRemain

    if count <= 0 and userTime.pickRemain != 0:
        await ctx.reply(UniMessage().text(la.err.invalid_catch_count.format(count)))
        return

    count = min(userTime.pickRemain, count)
    count = max(0, count)

    group_id: int | None = None

    if isinstance(ctx, GroupContext):
        group_id = ctx.event.group_id

    pickResult = await pickAwards(session, uid, count)
    pickEvent = PicksEvent(uid, group_id, pickResult, session)

    await root.emit(pickEvent)

    preEvent = await save_picks(
        pickResult=pickResult,
        group_id=group_id,
        uid=uid,
        session=session,
        userTime=userTime,
    )

    await root.emit(preEvent)
    await session.commit()

    # 此后数据库被关闭，发送数据
    if len(preEvent.picks.awards) > 0:
        await sendPickMessage(ctx, preEvent)
    else:
        await ctx.reply(await render_catch_failed_message(CatchMesssage(
            username=await ctx.getSenderName(),
            slot_remain=userTime.pickRemain,
            slot_sum=userTime.pickMax,
            next_time=userTime.pickLastUpdated + userTime.interval - time.time()
        )))
    return preEvent


@listenOnebot()
@matchAlconna(
    Alconna("re:(抓小哥|zhua|抓抓)", Arg("count", int, flags=[ArgFlag.OPTIONAL]))
)
@withLoading(la.loading.zhua)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, result: Arparma):
    # logger.info(result.query[int]("count"))
    count = result.query[int]("count")

    if count is None:
        count = 1

    user = await get_uid_by_qqid(session, ctx.getSenderId())
    await picks(ctx, session, user, count)


@listenOnebot()
@matchRegex("^(狂抓|kz|狂抓小哥)$")
@withLoading(la.loading.kz)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, _):
    user = await get_uid_by_qqid(session, ctx.getSenderId())
    await picks(ctx, session, user)


@listenOnebot()
@matchLiteral("是")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    flags_before = await get_user_flags(session, uid)
    await add_user_flag(session, uid, "是")
    utime = await calculateTime(session, uid)

    if utime.pickRemain > 0:
        await picks(ctx, session, uid, 1)  # 抓一次给他看
    elif "是" not in flags_before:
        await ctx.reply("收到。", ref=True)
    else:
        await ctx.reply("是", ref=True, at=False)

    await session.commit()
