from src.common.fast_import import *
from src.components.ref_book import skin_book


@listenOnebot()
@matchAlconna(Alconna("re:(更换|改变|替换|切换)(小哥)?(皮肤)", Arg("name", str)))
@withSessionLock()
async def _(
    ctx: GroupContext | PrivateContext,
    session: AsyncSession,
    result: Arparma,
):
    name = result.query[str]("name")
    user = await get_uid_by_qqid(session, ctx.getSenderId())

    if name is None:
        return

    award = await get_aid_by_name(session, name)
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


@listenOnebot()
@matchAlconna(
    Alconna(
        "re:(pfjd|pftj|皮肤图鉴|皮肤进度|皮肤收集进度)"
    )
)
@withSessionLock()
@withLoading()
async def _(ctx: OnebotContext, session: AsyncSession, _: Arparma):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    query = (
        select(Skin.data_id, Skin.image, Skin.name, Award.name, Level.color_code)
        .join(Award, Award.data_id == Skin.applied_award_id)
        .join(Level, Level.data_id == Award.level_id)
        .order_by(-Level.sorting_priority, Level.weight, Skin.applied_award_id)
    )
    skins = (await session.execute(query)).tuples().all()

    query = select(OwnedSkin.skin_id).filter(OwnedSkin.user_id == uid)
    owned = (await session.execute(query)).scalars().all()

    query = select(UsedSkin.skin_id).filter(UsedSkin.user_id == uid)
    used = (await session.execute(query)).scalars().all()

    _boxes: list[tuple[str, str, str, str, str]] = []
    _un = (
        la.disp.award_unknown_name,
        "",
        "",
        "#696361",
        "./res/blank_placeholder.png",
    )

    for sid, img, sname, aname, color in skins:
        if sid not in owned:
            _boxes.append(_un)
            continue

        notation = la.disp.skin_using if sid in used else ""
        _boxes.append((sname, aname, notation, color, img))

    boxes: list[PILImage] = []
    for box in _boxes:
        boxes.append(await skin_book(*box))

    imgout = await combineABunchOfImage(
        paddingX=0,
        paddingY=0,
        images=boxes,
        rowMaxNumber=6,
        background="#9B9690",
        horizontalAlign="top",
        verticalAlign="left",
        marginLeft=30,
        marginRight=30,
        marginBottom=30,
        marginTop=30,
    )

    await ctx.reply(UniMessage().image(raw=imageToBytes(imgout)))
