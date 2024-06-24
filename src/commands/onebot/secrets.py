from src.imports import *


@listenOnebot()
@matchLiteral("给小哥不是给")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    query = select(Skin.data_id).filter(Skin.name == "不是给")
    skin = (await session.execute(query)).scalar_one_or_none()
    query = select(Award.data_id).filter(Award.name == "给小哥")
    aid = (await session.execute(query)).scalar_one()

    if skin is None:
        logger.warning(la.err.log_no_gei)
        return

    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    if await have_skin(session, uid, skin) == False:
        await ctx.send(UniMessage().text("获取成功！"))
    if await using_skin(session, uid, aid) != skin:
        await ctx.send(UniMessage().text("切换成功！"))
    await give_skin(session, uid, skin)
    await set_skin(session, uid, skin)
    await session.commit()


@listenOnebot()
@matchLiteral("给小哥是给")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    query = select(Award.data_id).filter(Award.name == "给小哥")
    aid = (await session.execute(query)).scalar_one()
    if await using_skin(session, uid, aid) != None:
        await ctx.send(UniMessage().text("切换成功！"))
    await clear_skin(session, uid, aid)
    await session.commit()


@listenOnebot()
@matchLiteral("哇嘎嘎嘎")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    # 在数据库中，小光和小望的 ID
    guang = 1
    wang = 4

    guang_sto = await get_statistics(session, uid, guang)
    wang_sto = await get_statistics(session, uid, wang)

    if guang_sto > 0 and wang_sto > 0:
        ye_query = select(Skin.data_id).filter(
            Skin.name == "耶", Skin.applied_award_id == 75
        )
        skin = (await session.execute(ye_query)).scalar_one_or_none()

        if skin is None:
            logger.warning("请升级到最新数据库，才有耶皮肤")
            return

        if await have_skin(session, uid, skin) == False:
            await ctx.send(UniMessage().text("获取成功！"))
        await give_skin(session, uid, skin)
        await session.commit()