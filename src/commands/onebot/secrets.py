from src.common.fast_import import *


@listenOnebot()
@matchLiteral("给小哥不是给")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession):
    query = select(Skin.data_id).filter(Skin.name == "不是给")
    skin = (await session.execute(query)).scalar_one_or_none()

    if skin is None:
        logger.warning(la.err.log_no_gei)
        return
    
    user = await qid2did(session, ctx.getSenderId())
    await give_skin(session, user, skin)
    await set_skin(session, user, skin)
    await session.commit()
