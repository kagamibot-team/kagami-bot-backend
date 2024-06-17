from src.common.fast_import import *


async def switch_in_skin_list(session: AsyncSession, user: int, skins: list[tuple[int, str]]):
    if len(skins) == 0:
        return None

    query = select(UsedSkin.skin_id).filter(UsedSkin.user_id == user)

    try:
        used = (await session.execute(query)).one_or_none()
    except MultipleResultsFound:
        logger.warning(la.warn.log_multi_skin.format(user))
        await clear_skin(session, user)
        return None
    
    if used is None:
        await set_skin(session, user, skins[0][0])
        return skins[0]
    
    for i, (id, _) in enumerate(skins):
        if id == used[0]:
            if i == len(skins) - 1:
                await clear_skin(session, user)
                return None
            
            await set_skin(session, user, skins[i + 1][0])
            return skins[i + 1]
    
    logger.warning(la.warn.log_use_skin_not_exists.format(user))
    await clear_skin(session, user)
    return None


@listenOnebot()
@matchAlconna(Alconna("re:(更换|改变|替换|切换)(小哥)?(皮肤)", Arg("name", str)))
@withSessionLock()
async def _(
    ctx: GroupContext | PrivateContext,
    session: AsyncSession,
    result: Arparma,
):
    name = result.query[str]("name")
    user = await qid2did(session, ctx.getSenderId())

    if name is None:
        return

    query = select(Award.data_id).filter(Award.name == name)
    award = (await session.execute(query)).scalar_one_or_none()

    if award is None:
        query = select(Award.data_id).filter(
            Award.alt_names.any(AwardAltName.name == name)
        )
        award = (await session.execute(query)).scalar_one_or_none()

    if award is None:
        query = select(Skin.data_id).filter(Skin.name == name)
        skin = (await session.execute(query)).scalar_one_or_none()
        if skin is None:
            query = select(Skin.data_id).filter(
                Skin.alt_names.any(SkinAltName.name == name)
            )
            skin = (await session.execute(query)).scalar_one_or_none()

        if skin is None:
            await ctx.reply(UniMessage().text(la.err.not_found.format(name)))
            return

        query = select(OwnedSkin.data_id).filter(
            OwnedSkin.user_id == user, OwnedSkin.skin_id == skin
        )
        owned = (await session.execute(query)).scalar_one_or_none()
        if owned is None:
            await ctx.reply(UniMessage().text(la.err.not_own.format(name)))
            return

        await set_skin(session, user, skin)
        await ctx.reply(UniMessage().text(la.msg.skin_set.format(name)))
        await session.commit()
        return

    query = (
        select(OwnedSkin.skin_id, Skin.name)
        .join(Skin, OwnedSkin.skin_id == Skin.data_id)
        .filter(OwnedSkin.user_id == user)
        .filter(Skin.applied_award_id == award)
    )
    skins = (await session.execute(query)).tuples()
    skin = await switch_in_skin_list(session, user, list(skins))

    if skin is None:
        await ctx.reply(UniMessage().text(la.msg.skin_set_default.format(name)))
    else:
        await ctx.reply(UniMessage().text(la.msg.skin_set_2.format(name, skin[1])))
    
    await session.commit()
