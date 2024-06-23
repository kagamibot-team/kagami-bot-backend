from src.imports import *


@listenOnebot()
@matchLiteral("给小哥不是给")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    query = select(Skin.data_id).filter(Skin.name == "不是给")
    skin = (await session.execute(query)).scalar_one_or_none()

    if skin is None:
        logger.warning(la.err.log_no_gei)
        return

    user = await get_uid_by_qqid(session, ctx.getSenderId())
    await give_skin(session, user, skin)
    await set_skin(session, user, skin)
    await session.commit()


@listenOnebot()
@matchLiteral("给小哥是给")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    query = select(Award.data_id).filter(Award.name == "给小哥")
    aid = (await session.execute(query)).scalar_one()
    await clear_skin(session, uid, aid)
    await session.commit()
