from src.common.fast_import import *


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

    award = await getAidByName(session, name)
    if award is None:
        skin = await get_sid_by_name(session, name)

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

    skin = await switch_skin_of_award(session, user, award)

    if skin is None:
        await ctx.reply(UniMessage().text(la.msg.skin_set_default.format(name)))
    else:
        await ctx.reply(UniMessage().text(la.msg.skin_set_2.format(name, skin[1])))
    
    await session.commit()
