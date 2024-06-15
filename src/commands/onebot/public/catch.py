from dataclasses import dataclass
import time
import PIL
import PIL.Image
from nonebot import logger
from nonebot_plugin_alconna import Alconna, UniMessage
from arclet.alconna import Arg, ArgFlag, Arparma
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.data.awards import AwardInfo, getAwardInfo
from src.common.data.users import qid2did
from src.common.draw import imageToBytes
from src.common.draw.images import verticalPile

from src.components import catch



from ....logic.catch import Pick, PickResult, pickAwards

from ....events import root
from ....events.context import OnebotContext
from ....events.decorator import listenOnebot, matchAlconna, matchRegex, withSessionLock

from ...basics.loading import withLoading
from src.common.db import get_session


@dataclass
class CatchResultMessageEvent:
    ctx: OnebotContext
    pickResult: PickResult
    picks: list[tuple[Pick, AwardInfo]]


async def prepareForMessage(ctx: OnebotContext, pickResult: PickResult):
    session = get_session()

    async with session.begin():
        begin = time.time()
        user = await qid2did(session, ctx.getSenderId())
        logger.debug("获取用户花费了%f秒" % (time.time() - begin))

        picks = [
            (
                pick,
                await getAwardInfo(
                    session, user, pick.awardId
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


@listenOnebot()
@matchAlconna(Alconna("re:(抓小哥|zhua)", Arg("count", int, flags=[ArgFlag.OPTIONAL])))
@withLoading("正在抓小哥...")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, result: Arparma):
    count = result.query[int]("count")

    if count is None:
        count = 1

    user = await qid2did(session, ctx.getSenderId())

    pickResult = await pickAwards(session, user, count)
    await session.commit()

    await root.emit(pickResult)
    await root.emit(await prepareForMessage(ctx, pickResult))


@listenOnebot()
@matchRegex("^(狂抓|kz)$")
@withLoading("正在抓小哥...")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, _):
    begin = time.time()
    user = await qid2did(session, ctx.getSenderId())
    logger.debug(f"获取用户信息花了 {time.time() - begin} 秒")

    begin = time.time()
    pickResult = await pickAwards(session, user, -1)
    await session.commit()
    logger.debug(f"抓小哥总共耗时 {time.time() - begin} 秒")

    await root.emit(pickResult)
    await root.emit(await prepareForMessage(ctx, pickResult))
