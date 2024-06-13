from dataclasses import dataclass
import time
from typing import Any, cast
from nonebot_plugin_alconna import Alconna, UniMessage
from arclet.alconna import Arg, ArgFlag, Arparma
from nonebot_plugin_orm import AsyncSession, get_session

from ....images.components import display_box

from ....putils.draw import imageToBytes

from ....putils.typing import Session

from ....models.models import *
from ....models.crud import (
    getAllSkins,
    getAwardById,
    getAwardDescription,
    getAwardImage,
    getUser,
    getUserById,
)

from ....logic.catch import Pick, PickResult, pickAwards

from .....catch.events import root

from ....events.context import OnebotGroupMessageContext, OnebotPrivateMessageContext
from ....events.decorator import (
    listenOnebot,
    matchAlconna,
    matchRegex,
    withSessionLock,
)
from ...basics.loading import withLoading


@dataclass
class AwardInfo:
    awardId: int
    awardImg: str
    awardName: str
    awardDescription: str
    levelName: str
    color: str


@dataclass
class CatchResultMessageEvent:
    ctx: OnebotGroupMessageContext[Any] | OnebotPrivateMessageContext[Any]
    pickResult: PickResult
    picks: list[tuple[Pick, AwardInfo]]


async def prepareForMessage(
    ctx: OnebotGroupMessageContext | OnebotPrivateMessageContext, pickResult: PickResult
):
    session = get_session()

    async with session.begin():
        user = await getUserById(session, pickResult.uid)
        picks = [
            (
                pick,
                await GetAwardInfo(
                    session, user, await getAwardById(session, pick.awardId)
                ),
            )
            for pick in pickResult.picks
        ]

    return CatchResultMessageEvent(ctx, pickResult, picks)


async def GetAwardInfo(session: Session, user: User, award: Award):
    return AwardInfo(
        awardId=cast(int, award.data_id),
        awardImg=await getAwardImage(session, user, award),
        awardName=award.name,
        awardDescription=await getAwardDescription(session, user, award),
        levelName=award.level.name,
        color=award.level.color_code,
    )


@root.listen(CatchResultMessageEvent)
async def _(e: CatchResultMessageEvent):
    pickResult = e.pickResult

    counts = sum([p.countDelta for p in pickResult.picks])
    money = sum([p.money for p in pickResult.picks])

    picks = e.picks

    deltaTime = int(pickResult.timeToNextPick - time.time())

    seconds = deltaTime % 60
    minutes = int(deltaTime / 60) % 60
    hours = int(deltaTime / 3600)

    timeStr = f"{seconds}秒"
    if hours > 0:
        timeStr = f"{hours}小时{minutes}分钟" + timeStr
    elif minutes > 0:
        timeStr = f"{minutes}分钟" + timeStr

    if len(picks) == 0:
        await e.ctx.send(UniMessage().text(f"小哥还没长成，请再等{timeStr}吧！"))

    msg = (
        UniMessage()
        .text(
            f"剩余抓小哥的次数：{pickResult.restPickCount}/{pickResult.maxPickCount}\n"
            f"下次次数恢复还需要{timeStr}\n"
            f"你刚刚一共抓了 {counts} 只小哥，并得到了 {int(money)} 薯片\n"
            f"现在，你一共有 {pickResult.moneyAfterPick} 薯片\n"
        )
        .text("\n".join(pickResult.extraMessages))
    )

    for pick, awardInfo in picks:
        msg += (
            UniMessage()
            .image(
                raw=imageToBytes(
                    await display_box(
                        color=awardInfo.color,
                        central_image=awardInfo.awardImg,
                        new=pick.countBefore == 0,
                    )
                )
            )
            .text(
                f"【{awardInfo.levelName}】{awardInfo.awardName} (x{pick.countDelta}) → {pick.countBefore + pick.countDelta}\n"
                f"{awardInfo.awardDescription}\n\n"
            )
        )

    await e.ctx.send(msg)


@listenOnebot(root)
@matchAlconna(Alconna("re:(抓小哥|zhua)", Arg("count", int, flags=[ArgFlag.OPTIONAL])))
@withLoading()
@withSessionLock()
async def _(
    ctx: OnebotGroupMessageContext | OnebotPrivateMessageContext,
    session: AsyncSession,
    result: Arparma,
):
    count = result.query[int]("count")

    if count is None:
        count = 1

    user = await getUser(session, ctx.getSenderId())

    pickResult = await pickAwards(session, user, count)
    await session.commit()

    await root.emit(pickResult)
    await root.emit(await prepareForMessage(ctx, pickResult))


@listenOnebot(root)
@matchRegex("^(狂抓|kz)$")
@withLoading()
@withSessionLock()
async def _(
    ctx: OnebotGroupMessageContext | OnebotPrivateMessageContext,
    session: AsyncSession,
    _,
):
    user = await getUser(session, ctx.getSenderId())
    pickResult = await pickAwards(session, user, -1)
    await session.commit()

    await root.emit(pickResult)
    await root.emit(await prepareForMessage(ctx, pickResult))
