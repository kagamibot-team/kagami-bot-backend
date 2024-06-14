from dataclasses import dataclass
import time
import PIL
import PIL.Image
from nonebot_plugin_alconna import Alconna, UniMessage
from arclet.alconna import Arg, ArgFlag, Arparma
from nonebot_plugin_orm import AsyncSession, get_session

from ....putils.draw import imageToBytes
from ....putils.draw.images import verticalPile

from ....images.components import catch

from ....models.data import AwardInfo, GetAwardInfo
from ....models.models import *
from ....models.crud import getAwardById, getUser, getUserById

from ....logic.catch import Pick, PickResult, pickAwards

from ....events import root
from ....events.context import OnebotContext
from ....events.decorator import listenOnebot, matchAlconna, matchRegex, withSessionLock

from ...basics.loading import withLoading


@dataclass
class CatchResultMessageEvent:
    ctx: OnebotContext
    pickResult: PickResult
    picks: list[tuple[Pick, AwardInfo]]


async def prepareForMessage(ctx: OnebotContext, pickResult: PickResult):
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
        await e.ctx.reply(UniMessage().text(f"小哥还没长成，请再等{timeStr}吧！"))
        return

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

    boxes: list[PIL.Image.Image] = []

    for pick, info in picks:
        image = await catch(
            title=info.awardName,
            description=info.awardDescription,
            image=info.awardImg,
            stars=info.levelName,
            color=info.color,
            new=pick.countBefore == 0,
            notation=f"x{pick.countDelta}",
        )

        boxes.append(image)

    img = await verticalPile(boxes, 33, "left", "#EEEBE3", 80, 80, 80, 80)

    await e.ctx.reply(msg + UniMessage().image(raw=imageToBytes(img)))


@listenOnebot(root)
@matchAlconna(Alconna("re:(抓小哥|zhua)", Arg("count", int, flags=[ArgFlag.OPTIONAL])))
@withLoading("正在抓小哥...")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, result: Arparma):
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
@withLoading("正在抓小哥...")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, _):
    user = await getUser(session, ctx.getSenderId())
    pickResult = await pickAwards(session, user, -1)
    await session.commit()

    await root.emit(pickResult)
    await root.emit(await prepareForMessage(ctx, pickResult))
