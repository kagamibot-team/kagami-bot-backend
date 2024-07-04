import time


from src.imports import *
from src.logic.catch import pickAwards
from src.logic.catch_time import calculateTime, updateUserTime


async def sendPickMessage(ctx: OnebotMessageContext, e: PrePickMessageEvent):
    pickDisplay = e.displays
    userTime = e.userTime
    timeToNextPick = userTime.pickLastUpdated + userTime.interval

    money = e.picks.money

    deltaTime = int(timeToNextPick - time.time())

    seconds = deltaTime % 60
    minutes = int(deltaTime / 60) % 60
    hours = int(deltaTime / 3600)

    timeStr = f"{seconds}{la.unit.second}"
    if hours > 0:
        timeStr = f"{minutes}{la.unit.minute}" + timeStr
    elif minutes > 0:
        timeStr = f"{hours}{la.unit.hour}{minutes}{la.unit.minute}" + timeStr

    if len(pickDisplay) == 0:
        await ctx.reply(UniMessage().text(la.err.catch_not_available.format(timeStr)))
        return

    titles: list[PIL.Image.Image] = []
    boxes: list[PIL.Image.Image] = []

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderNameInGroup()

    titles.append(
        await getTextImage(
            text=f"{name} 的一抓！",
            color="#63605C",
            font=Fonts.JINGNAN_BOBO_HEI,
            font_size=96,
            width=800,
        )
    )
    titles.append(
        await getTextImage(
            text=(
                f"本次获得{int(money)}{la.unit.money}，"
                f"目前共有{int(e.moneyUpdated)}{la.unit.money}。"
            ),
            width=800,
            color="#9B9690",
            font=Fonts.ALIMAMA_SHU_HEI,
            font_size=28,
        )
    )
    titles.append(
        await getTextImage(
            text=(
                f"剩余次数： {userTime.pickRemain}/{userTime.pickMax}，"
                f"距下次次数恢复还要{timeStr}。"
            ),
            width=800,
            color="#9B9690",
            font=Fonts.ALIMAMA_SHU_HEI,
            font_size=28,
        )
    )

    for display in pickDisplay.values():
        image = await catch(
            title=display.name,
            description=display.description,
            image=display.image,
            stars=display.level,
            color=display.color,
            new=display.pick.beforeStats == 0,
            notation=f"+{display.pick.delta}",
        )
        boxes.append(image)

    area_title = await verticalPile(titles, 0, "left", "#EEEBE3", 0, 0, 0, 0)
    area_box = await verticalPile(boxes, 30, "left", "#EEEBE3", 0, 0, 0, 0)
    img = await verticalPile(
        [area_title, area_box], 30, "left", "#EEEBE3", 60, 80, 80, 80
    )
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))


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
        before = await add_storage(session, uid, aid, pick.delta)

        query = (
            select(
                Award.name,
                Award.img_path,
                Award.description,
                Level.name,
                Level.color_code,
            )
            .filter(Award.data_id == aid)
            .join(Level, Award.level_id == Level.data_id)
        )
        name, image, description, level, color = (
            (await session.execute(query)).tuples().one()
        )

        preEvent.displays[aid] = PickDisplay(
            name=name,
            image=image,
            description=description,
            level=level,
            color=color,
            beforeStorage=before,
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
    await sendPickMessage(ctx, preEvent)


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
