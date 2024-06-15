from nonebot import logger
from src.db.data import obtainSkin
from src.db.crud import getSkinByName, getUser, setSkin
from ....utils.typing import Session
from ....events.context import OnebotContext
from ....events import root
from ....events.decorator import listenOnebot, matchLiteral, withSessionLock


@listenOnebot(root)
@matchLiteral("给小哥不是给")
@withSessionLock()
async def _(ctx: OnebotContext, session: Session):
    skin = await getSkinByName(session, "不是给")

    if skin is None:
        logger.warning("这个世界没有给小哥。")
        return
    
    user = await getUser(session, ctx.getSenderId())
    await obtainSkin(session, user, skin)
    await setSkin(session, user, skin)
