import time


from src.common.fast_import import *
from src.logic.catch import pickAwards
from src.logic.catch_time import calculateTime, updateUserTime


async def sendPickMessage(ctx: OnebotContext, e: PrePickMessageEvent):
    pickDisplay = e.displays
    userTime = e.userTime
    timeToNextPick = userTime.pickLastUpdated + userTime.interval

    counts = sum([p.pick.delta for _, p in pickDisplay.items()])
    money = e.picks.money

    deltaTime = int(timeToNextPick - time.time())

    seconds = deltaTime % 60
    minutes = int(deltaTime / 60) % 60
    hours = int(deltaTime / 3600)

    timeStr = f"{seconds}秒"
    if hours > 0:
        timeStr = f"{hours}小时{minutes}分钟" + timeStr
    elif minutes > 0:
        timeStr = f"{minutes}分钟" + timeStr

    if len(pickDisplay) == 0:
        await ctx.reply(UniMessage().text(f"小哥还没长成，请再等{timeStr}吧！"))
        return

    msg = UniMessage().text(
        f"剩余抓小哥的次数：{userTime.pickRemain}/{userTime.pickMax}\n"
        f"下次次数恢复还需要{timeStr}\n"
        f"你刚刚一共抓了 {counts} 只小哥，并得到了 {int(money)} 薯片\n"
        f"现在，你一共有 {int(e.moneyUpdated)} 薯片\n"
    )

    boxes: list[PIL.Image.Image] = []

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

    img = await verticalPile(boxes, 33, "left", "#EEEBE3", 80, 80, 80, 80)
    await ctx.reply(msg + UniMessage().image(raw=imageToBytes(img)))


async def picks(
    ctx: OnebotContext, session: AsyncSession, uid: int, count: int | None = None
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
        ctx (OnebotContext): 抓小哥的上下文
        session (AsyncSession): 所开启的数据库会话，将会在中途关闭
        uid (int): 数据库中的用户 ID
        count (int | None, optional): 抓的次数，如果为 None，则尽可能多抓
    """

    userTime = await calculateTime(session, uid)
    count = count or userTime.pickRemain
    count = min(userTime.pickMax, count)
    count = max(0, count)

    pickResult = await pickAwards(session, uid, count)
    pickEvent = PicksEvent(uid, pickResult, session)

    await root.emit(pickEvent)

    preEvent = PrePickMessageEvent(pickResult, {}, uid, session, userTime)

    # 在这里进行了数据库库存的操作
    spent_count = 0

    for aid in pickResult.awards.keys():
        pick = pickResult.awards[aid]
        spent_count += pick.delta
        before = await addStorage(session, uid, aid, pick.delta)

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
            (await session.execute(query)).one().tuple()
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
        .values(money=User.money + 1)
        .returning(User.money)
    )
    res = (await session.execute(query)).scalar_one()
    preEvent.moneyUpdated = res

    await root.emit(preEvent)
    await session.commit()

    # 此后数据库被关闭，发送数据
    await sendPickMessage(ctx, preEvent)


@listenOnebot()
@matchAlconna(
    Alconna("re:(抓小哥|zhua|抓抓)", Arg("count", int, flags=[ArgFlag.OPTIONAL]))
)
@withLoading("正在抓小哥...")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, result: Arparma):
    count = result.query[int]("count") or 1
    user = await qid2did(session, ctx.getSenderId())
    await picks(ctx, session, user, count)


@listenOnebot()
@matchRegex("^(狂抓|kz|狂抓小哥)$")
@withLoading("正在抓小哥...")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, _):
    user = await qid2did(session, ctx.getSenderId())
    await picks(ctx, session, user)
