from nonebot_plugin_alconna import Alconna
from arclet.alconna import Arg, ArgFlag, Arparma
from nonebot_plugin_orm import AsyncSession

from ....messages.texts import caughtMessage

from ....models.data import handlePick

from ....events.context import OnebotGroupMessageContext, OnebotPrivateMessageContext
from ....events.manager import EventManager
from ...basics.decorator import (
    listenOnebot,
    matchAlconna,
    matchRegex,
    withSessionLock,
)
from ...basics.loading import withLoading


catchEventManager = EventManager()


@listenOnebot(catchEventManager)
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

    picksResult = await handlePick(session, ctx.getSenderId(), count)
    await session.commit()
    message = await caughtMessage(picksResult)

    await ctx.bot.send(ctx.event, message)


@listenOnebot(catchEventManager)
@matchRegex("^(狂抓|kz)$")
@withLoading()
@withSessionLock()
async def _(
    ctx: OnebotGroupMessageContext | OnebotPrivateMessageContext,
    session: AsyncSession,
    _,
):
    picksResult = await handlePick(session, ctx.getSenderId(), -1)
    await session.commit()
    message = await caughtMessage(picksResult)

    await ctx.bot.send(ctx.event, message)
