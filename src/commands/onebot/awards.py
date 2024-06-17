import pathlib


from src.common.fast_import import *


@listenOnebot()
@matchAlconna(Alconna("re:(展示|zhanshi|zs)", Arg("name", str)))
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, result: Arparma):
    name = result.query[str]("name")
    user = await qid2did(session, ctx.getSenderId())

    if name is None:
        return

    award = await getAidByName(session, name)

    if award is None:
        await ctx.reply(UniMessage(f"没有叫 {name} 的小哥"))
        return

    if await getStatistics(session, user, award) <= 0:
        await ctx.reply(UniMessage(f"你还没有遇到过叫做 {name} 的小哥"))
        return

    info = await getAwardInfo(session, user, award)
    nameDisplay = info.awardName

    if info.skinName is not None:
        nameDisplay += f"[{info.skinName}]"

    await ctx.reply(
        UniMessage()
        .text(nameDisplay + f"【{info.levelName}】")
        .image(path=pathlib.Path(info.awardImg))
        .text(f"\n{info.awardDescription}")
    )


async def _combine_cells(imgs: list[PILImage], marginTop: int = 0):
    return await combineABunchOfImage(
        paddingX=0,
        paddingY=0,
        images=imgs,
        rowMaxNumber=6,
        background="#9B9690",
        horizontalAlign="top",
        verticalAlign="left",
        marginLeft=30,
        marginRight=30,
        marginBottom=30,
        marginTop=marginTop,
    )


async def _title(lname: str, lcolor: str):
    return await drawABoxOfText(
        f"{lname}",
        lcolor,
        textFont(Fonts.HARMONYOS_SANS_BLACK, 60),
        background="#9B9690",
    )


async def _get_levels(session: AsyncSession):
    query = select(Level.data_id, Level.name, Level.color_code).order_by(
        -Level.sorting_priority, Level.weight
    )
    return (await session.execute(query)).tuples()


async def _get_awards(session: AsyncSession, lid: int):
    query = select(Award.data_id, Award.name, Award.img_path).filter(
        Award.level_id == lid
    )
    return (await session.execute(query)).tuples().all()


async def _get_others(session: AsyncSession, uid: int):
    query = select(Skin.applied_award_id, Skin.image).filter(
        Skin.owned_skins.any(OwnedSkin.user_id == uid)
    )
    skins = (await session.execute(query)).tuples().all()
    skins = {_id: img for _id, img in skins}

    query = select(StorageStats.target_award_id, StorageStats.count).filter(
        StorageStats.target_user_id == uid
    )
    storages = (await session.execute(query)).tuples().all()
    storages = {_id: count for _id, count in storages}

    query = select(UsedStats.target_award_id, UsedStats.count).filter(
        UsedStats.target_user_id == uid
    )
    used = (await session.execute(query)).tuples().all()
    used = {_id: count for _id, count in used}

    return skins, storages, used


@listenOnebot()
@matchAlconna(Alconna("re:(zhuajd|抓进度|抓小哥进度)"))
@withLoading("正在思考你遇到过的小哥……")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, __: Arparma):
    uid = await qid2did(session, ctx.getSenderId())
    if uid is None:
        return

    levels = await _get_levels(session)
    skins, storages, used = await _get_others(session, uid)

    baseImgs: list[PILImage] = []
    for lid, lname, lcolor in levels:
        awards = await _get_awards(session, lid)
        if len(awards) == 0:
            continue
        imgs: list[PILImage] = []
        met_sums = 0
        for aid, name, img in awards:
            color = lcolor
            sto = storages[aid] if aid in storages.keys() else 0
            use = used[aid] if aid in used.keys() else 0

            if sto + use == 0:
                img = "./res/blank_placeholder.png"
                name = "???"
                color = "#696361"
            elif aid in skins.keys():
                img = skins[aid]
                met_sums += 1
            else:
                met_sums += 1

            imgs.append(await ref_book_box(name, "", color, img))

        baseImgs.append(await _title(f"{lname} {met_sums}/{len(awards)}", lcolor))
        baseImgs.append(await _combine_cells(imgs))

    img = await verticalPile(baseImgs, 15, "left", "#9B9690", 120, 60, 60, 60)
    await ctx.reply(UniMessage().image(raw=imageToBytes(img)))


@listenOnebot()
@matchAlconna(Alconna("re:(kc|抓库存|抓小哥库存)"))
@withLoading("正在数小哥……")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, __: Arparma):
    uid = await qid2did(session, ctx.getSenderId())
    if uid is None:
        return

    levels = await _get_levels(session)
    skins, storages, used = await _get_others(session, uid)

    imgs: list[PILImage] = []
    for lid, _, lcolor in levels:
        awards = await _get_awards(session, lid)
        _imgs: list[tuple[int, PILImage]] = []

        if len(awards) == 0:
            continue
        for aid, name, img in awards:
            color = lcolor
            sto = storages[aid] if aid in storages.keys() else 0
            use = used[aid] if aid in used.keys() else 0

            if sto + use == 0:
                continue
            if aid in skins.keys():
                img = skins[aid]

            _imgs.append((sto, await ref_book_box(name, str(sto), color, img)))
        
        _imgs.sort(key=lambda x: -x[0])
        imgs += [i[1] for i in _imgs]

    await ctx.reply(
        UniMessage().image(raw=imageToBytes(await _combine_cells(imgs, marginTop=60)))
    )


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna("re:(::所有小哥)"))
@withLoading("正在生成")
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, __: Arparma):
    levels = await _get_levels(session)

    baseImgs: list[PILImage] = []
    for lid, lname, lcolor in levels:
        awards = await _get_awards(session, lid)

        if len(awards) == 0:
            continue
        imgs: list[PILImage] = []
        for _, name, img in awards:
            color = lcolor
            imgs.append(await ref_book_box(name, "", color, img))

        baseImgs.append(await _title(lname, lcolor))
        baseImgs.append(await _combine_cells(imgs))

    img = await verticalPile(baseImgs, 15, "left", "#9B9690", 120, 60, 60, 60)
    await ctx.reply(UniMessage().image(raw=imageToBytes(img)))
