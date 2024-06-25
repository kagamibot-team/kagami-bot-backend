from src.imports import *


@listenOnebot()
@matchLiteral("给小哥不是给")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    query = select(Skin.data_id).filter(Skin.name == "不是给")
    not_sid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "给小哥")
    gei_aid = (await session.execute(query)).scalar_one_or_none()

    if gei_aid is None or not_sid is None:
        logger.warning(la.err.data_missing)
        return

    if await have_skin(session, uid, not_sid) == False:
        await ctx.send(UniMessage().text("获取成功！"))
    if await using_skin(session, uid, gei_aid) != not_sid:
        await ctx.send(UniMessage().text("切换成功！"))
    await give_skin(session, uid, not_sid)
    await set_skin(session, uid, not_sid)
    await session.commit()


@listenOnebot()
@matchLiteral("给小哥是给")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    query = select(Award.data_id).filter(Award.name == "给小哥")
    gei_aid = (await session.execute(query)).scalar_one_or_none()

    if gei_aid is None:
        logger.warning(la.err.data_missing)
        return
    
    if await using_skin(session, uid, gei_aid) != None:
        await ctx.send(UniMessage().text("切换成功！"))
    await clear_skin(session, uid, gei_aid)
    await session.commit()


@listenOnebot()
@matchLiteral("哇嘎嘎嘎")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    query = select(Skin.data_id).filter(Skin.name == "耶")
    ye_sid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "小光")
    hkr_aid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "小望")
    nzm_aid = (await session.execute(query)).scalar_one_or_none()

    if ye_sid is None or hkr_aid is None or nzm_aid is None:
        logger.warning(la.err.data_missing)
        return

    hkr_sto = await get_statistics(session, uid, hkr_aid)
    nzm_sto = await get_statistics(session, uid, nzm_aid)

    if hkr_sto == 0 or nzm_sto == 0:
        logger.info(la.err.data_not_satisfied)
        return
    
    if await have_skin(session, uid, ye_sid) == False:
        await ctx.send(UniMessage().text("获取成功！"))
    if await using_skin(session, uid, ye_sid) != ye_sid:
        await ctx.send(UniMessage().text("切换成功！"))
    await give_skin(session, uid, ye_sid)
    await set_skin(session, uid, ye_sid)
    await session.commit()


@listenOnebot()
@matchRegex(r"[\s\S]*(金|暴力|[Ss][Ee][Xx])[\s\S]*")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, _):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    query = select(Skin.data_id).filter(Skin.name == "三要素")
    kbs_sid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "富哥")
    kin_aid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "凹小哥")
    bou_aid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "小真寻&小美波里")
    sex_aid = (await session.execute(query)).scalar_one_or_none()

    if kbs_sid is None or kin_aid is None or bou_aid is None or sex_aid is None:
        logger.warning(la.err.data_missing)
        return
    
    kin_sto = await get_statistics(session, uid, kin_aid)
    bou_sto = await get_statistics(session, uid, bou_aid)
    sex_sto = await get_statistics(session, uid, sex_aid)

    if kin_sto == 0 or bou_sto == 0 or sex_sto == 0:
        logger.info(la.err.data_not_satisfied)
        return

    if await have_skin(session, uid, kbs_sid) == False:
        await ctx.send(UniMessage().text("获取成功！"))
    if await using_skin(session, uid, kbs_sid) != kbs_sid:
        await ctx.send(UniMessage().text("切换成功！"))
    await give_skin(session, uid, kbs_sid)
    await set_skin(session, uid, kbs_sid)
    await session.commit()