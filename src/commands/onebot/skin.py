from src.imports import *
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

        if not await do_user_have_skin(session, user, skin):
            await ctx.reply(UniMessage().text(la.err.not_own.format(name)))
            return

        await use_skin(session, user, skin)
        await ctx.reply(UniMessage().text(la.msg.skin_set.format(name)))
        await session.commit()
        return

    skin = await switch_skin_of_award(session, user, award)

    if skin is None:
        await ctx.reply(UniMessage().text(la.msg.skin_set_default.format(name)))
    else:
        await ctx.reply(UniMessage().text(la.msg.skin_set_2.format(name, await get_skin_name(session, skin))))

    await session.commit()


@listenOnebot()
@matchAlconna(Alconna("re:(pfjd|pftj|皮肤图鉴|皮肤进度|皮肤收集进度)"))
@withLoading()
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, _: Arparma):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    query = (
        select(Skin.data_id, Skin.image, Skin.name, Award.name, Award.level_id)
        .join(Award, Award.data_id == Skin.award_id)
    )
    skins = (await session.execute(query)).tuples().all()
    skins = sorted(skins, key=lambda s: level_repo.sorted_index[s[4]])

    query = select(SkinRecord.skin_id, SkinRecord.selected).filter(SkinRecord.user_id == uid)
    owned = dict((await session.execute(query)).tuples().all())

    _boxes: list[tuple[str, str, str, str, str]] = []
    _un = (
        la.disp.award_unknown_name,
        "",
        "",
        "#696361",
        "./res/blank_placeholder.png",
    )

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderNameInGroup()

    area_title = await getTextImage(
        text=f"{name} 的皮肤进度：",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=80,
        margin_bottom=30,
        width=216 * 6,
    )

    for sid, img, sname, aname, lid in skins:
        if sid not in owned:
            _boxes.append(_un)
            continue

        notation = la.disp.skin_using if owned[sid] == 1 else ""
        _boxes.append((sname, aname, notation, level_repo.levels[lid].color, img))

    boxes: list[PILImage] = []
    for box in _boxes:
        boxes.append(await skin_book(*box))

    area_box = await pileImages(images=boxes, rowMaxNumber=6, background="#9B9690")

    img = await verticalPile(
        [area_title, area_box], 15, "left", "#9B9690", 60, 60, 60, 60
    )
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "re:(所有|全部)皮肤",
        Arg("name", str, flags=[ArgFlag.OPTIONAL]),
    )
)
@withLoading()
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    name = res.query[str]("name")

    query = (
        select(Skin.name, Award.name, Skin.price, Award.level_id, Skin.image)
        .join(Award, Skin.award_id == Award.data_id)
    )

    if name:
        query1 = query.filter(Award.name == name)
        query2 = query.filter(Skin.name == name)
        query3 = query.join(AwardAltName, AwardAltName.award_id == Award.data_id).filter(AwardAltName.name == name)
        query4 = query.join(SkinAltName, SkinAltName.skin_id == Skin.data_id).filter(SkinAltName.name == name)

        skins1 = (await session.execute(query1)).tuples()
        skins2 = (await session.execute(query2)).tuples()
        skins3 = (await session.execute(query3)).tuples()
        skins4 = (await session.execute(query4)).tuples()

        skins = list(skins1) + list(skins2) + list(skins3) + list(skins4)
    else:
        skins = list((await session.execute(query)).tuples())

    skins = sorted(skins, key=lambda s: level_repo.sorted_index[s[3]])

    boxes: list[PILImage] = []
    for box in skins:
        boxes.append(await skin_book(box[0], box[1], str(box[2]), level_repo.levels[box[3]].color, box[4]))

    area_title = await getTextImage(
        text=f"全部 {len(skins)} 种皮肤：",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=80,
        margin_bottom=30,
        width=216 * 6,
    )

    area_box = await pileImages(images=boxes, rowMaxNumber=6, background="#9B9690")

    img = await verticalPile(
        [area_title, area_box], 15, "left", "#9B9690", 60, 60, 60, 60
    )
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))
