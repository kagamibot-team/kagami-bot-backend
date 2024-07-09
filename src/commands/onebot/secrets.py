from src.imports import *
import pathlib


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
        logger.error(la.err.data_missing)
        return

    if not await have_skin(session, uid, not_sid):
        await ctx.reply(UniMessage().text("获取成功！"), ref=True, at=False)
    if await using_skin(session, uid, gei_aid) != not_sid:
        await ctx.reply(UniMessage().text("切换成功！"), ref=True, at=False)
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
        logger.error(la.err.data_missing)
        return

    if await using_skin(session, uid, gei_aid) is not None:
        await ctx.reply(UniMessage().text("切换成功！"), ref=True, at=False)
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
        logger.error(la.err.data_missing)
        return

    hkr_sta = await get_statistics(session, uid, hkr_aid)
    nzm_sta = await get_statistics(session, uid, nzm_aid)

    if hkr_sta == 0 or nzm_sta == 0:
        logger.info(la.err.data_not_satisfied)
        return

    if not await have_skin(session, uid, ye_sid):
        await ctx.reply(UniMessage().text("获取成功！"), ref=True, at=False)
    if await using_skin(session, uid, ye_sid) != ye_sid:
        await ctx.reply(UniMessage().text("切换成功！"), ref=True, at=False)
    await give_skin(session, uid, ye_sid)
    await set_skin(session, uid, ye_sid)
    await session.commit()


@listenOnebot()
@matchRegex(r"[\s\S]*(金|暴力?|([Ss][Ee][Xx]|性))[\s\S]*")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, _):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    query = select(Skin.data_id, Skin.image).filter(Skin.name == "三要素")
    kbs_sid, kbs_img = (await session.execute(query)).tuples().one()
    query = select(Award.data_id).filter(Award.name == "三小哥")
    thr_aid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "富哥")
    kin_aid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "凹小哥")
    bou_aid = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "小真寻&小美波里")
    sex_aid = (await session.execute(query)).scalar_one_or_none()

    if (
        kbs_sid is None
        or thr_aid is None
        or kin_aid is None
        or bou_aid is None
        or sex_aid is None
    ):
        logger.error(la.err.data_missing)
        return

    kin_sta = await get_statistics(session, uid, kin_aid)
    bou_sta = await get_statistics(session, uid, bou_aid)
    sex_sta = await get_statistics(session, uid, sex_aid)

    if kin_sta == 0 or bou_sta == 0 or sex_sta == 0:
        logger.info(la.err.data_not_satisfied)
        return

    if not await have_skin(session, uid, kbs_sid):
        await ctx.reply(UniMessage().text("获取成功！"), ref=True, at=False)
    if await using_skin(session, uid, thr_aid) != kbs_sid:
        await ctx.reply(UniMessage().text("已装备！"), ref=True, at=False)
    await ctx.send(UniMessage().text("发现关键词，三小哥登场！！").image(path=pathlib.Path(kbs_img)))
    await give_skin(session, uid, kbs_sid)
    await set_skin(session, uid, kbs_sid)
    await session.commit()
