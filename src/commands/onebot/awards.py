import math
import pathlib
from typing import Sequence

from src.imports import *


@listenOnebot()
@matchAlconna(Alconna("re:(展示|zhanshi|zs)", Arg("name", str)))
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, result: Arparma):
    name = result.query[str]("name")
    user = await get_uid_by_qqid(session, ctx.getSenderId())

    if name is None:
        return

    award = await get_aid_by_name(session, name)

    if award is None:
        # 有可能是打成了皮肤的名字，试着匹配一下有没有皮肤有这个名字的

        sid = await get_sid_by_name(session, name)
        if sid is None:
            await ctx.reply(UniMessage(la.err.award_not_found.format(name)))
            return

        award = (
            await session.execute(
                select(Skin.applied_award_id)
                .filter(Skin.data_id == sid)
                .join(Award, Award.data_id == Skin.applied_award_id)
                .join(UsedSkin, UsedSkin.skin_id == sid)
                .filter(UsedSkin.user_id == user)
            )
        ).scalar_one_or_none()
        if award is None:
            await ctx.reply(UniMessage(la.err.award_not_found.format(name)))
            return

    if await get_statistics(session, user, award) <= 0:
        await ctx.reply(UniMessage(la.err.award_not_encountered_yet.format(name)))
        return

    info = await get_award_info(session, user, award)

    if info.skinName is not None:
        nameDisplay = la.disp.award_display_with_skin.format(
            info.awardName, info.skinName, info.levelName
        )
    else:
        nameDisplay = la.disp.award_display.format(info.awardName, info.levelName)

    await ctx.reply(
        UniMessage()
        .text(nameDisplay)
        .image(path=pathlib.Path(info.awardImg))
        .text(f"\n{info.awardDescription}")
    )


@listenOnebot()
@matchAlconna(Alconna("re:(展示|zhanshi|zs)条目", Arg("name", str)))
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, result: Arparma):
    name = result.query[str]("name")
    user = await get_uid_by_qqid(session, ctx.getSenderId())

    if name is None:
        return

    award = await get_aid_by_name(session, name)

    if award is None:
        await ctx.reply(UniMessage(la.err.award_not_found.format(name)))
        return

    if await get_statistics(session, user, award) <= 0:
        await ctx.reply(UniMessage(la.err.award_not_encountered_yet.format(name)))
        return

    info = await get_award_info(session, user, award)

    if info.skinName is not None:
        nameDisplay = "{0}[{1}]".format(info.awardName, info.skinName)
    else:
        nameDisplay = info.awardName

    image = await catch(
        title=nameDisplay,
        description=info.awardDescription,
        image=info.awardImg,
        stars=info.levelName,
        color=info.color,
        new=False,
        notation=str(await get_storage(session, user, award)),
    )

    await ctx.send(UniMessage().image(raw=imageToBytes(image)))


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        "re:(展示|zhanshi|zs)",
        ["::"],
        Arg("name", str),
        Arg("sname", str, flags=[ArgFlag.OPTIONAL]),
    )
)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, result: Arparma):
    name = result.query[str]("name")
    sname = result.query[str]("sname")

    if name is None:
        return

    aid = await get_aid_by_name(session, name)

    if aid is None:
        await ctx.reply(la.err.award_not_found.format(name))
        return

    query = select(Award.name, Award.description, Award.img_path).filter(
        Award.data_id == aid
    )
    dname, description, img_path = (await session.execute(query)).tuples().one()

    if sname is not None:
        sid = await get_sid_by_name(session, sname)
        if sid is None:
            await ctx.reply(la.err.skin_not_found.format(name))
            return

        query = select(Skin.name, Skin.extra_description, Skin.image).filter(
            Skin.data_id == sid, Skin.applied_award_id == aid
        )
        res = (await session.execute(query)).tuples().one_or_none()

        if res is None:
            await ctx.reply(la.err.invalid_skin_award_pair.format(name, sname))
            return

        dname, edesc, img_path = res
        description = edesc or description

    await ctx.reply(
        UniMessage()
        .text(dname)
        .image(path=pathlib.Path(img_path))
        .text(f"\n{description}")
    )


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna("re:(展示|zhanshi|zs)条目", ["::"], Arg("name", str)))
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, result: Arparma):
    name = result.query[str]("name")
    user = await get_uid_by_qqid(session, ctx.getSenderId())

    if name is None:
        return

    award = await get_aid_by_name(session, name)

    if award is None:
        await ctx.reply(UniMessage(la.err.award_not_found.format(name)))
        return

    info = await get_award_info(session, user, award)

    if info.skinName is not None:
        nameDisplay = "{0}[{1}]".format(info.awardName, info.skinName)
    else:
        nameDisplay = info.awardName

    image = await catch(
        title=nameDisplay,
        description=info.awardDescription,
        image=info.awardImg,
        stars=info.levelName,
        color=info.color,
        new=False,
        notation="",
    )

    await ctx.send(UniMessage().image(raw=imageToBytes(image)))


async def _combine_cells(imgs: list[PILImage], marginTop: int = 0):
    return await pileImages(
        paddingX=0,
        paddingY=0,
        images=imgs,
        rowMaxNumber=8,
        background="#9B9690",
        horizontalAlign="top",
        verticalAlign="left",
        marginLeft=30,
        marginRight=30,
        marginBottom=30,
        marginTop=marginTop,
    )


async def _get_levels(session: AsyncSession):
    query = select(Level.data_id, Level.name, Level.color_code, Level.weight).order_by(
        -Level.sorting_priority, Level.weight
    )
    return (await session.execute(query)).tuples().all()


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


def calc_progress(
    levels: Sequence[tuple[int, str, str, float]],
    met_sums: dict[int, int],
    awards: dict[int, Sequence[tuple[int, str, str]]],
):
    param: int = 10
    denominator: float = 0
    for _, name, _, lweight in levels:
        if lweight == 0:
            continue
        logger.info(
            "%s: %f ^ %f = %f"
            % (name, lweight, 1.0 / param, math.pow(lweight, 1.0 / param))
        )
        denominator += 1.0 / math.pow(lweight, 1.0 / param)

    progress: float = 0
    for lid, _, _, lweight in levels:
        if lweight == 0:
            continue
        numerator: float = 1.0 / math.pow(lweight, 1.0 / param)
        progress += numerator / denominator * (1.0 * met_sums[lid] / len(awards[lid]))

    return progress


@listenOnebot()
@matchAlconna(
    Alconna(
        "re:(zhuajd|抓进度|抓小哥进度)",
        Option(
            "等级",
            Arg("等级名字", str),
            alias=["--level", "级别", "-l", "-L"],
            compact=True,
        ),
    )
)
@withLoading(la.loading.zhuajd)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, res: Arparma):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    if uid is None:
        return

    levels = await _get_levels(session)
    skins, storages, used = await _get_others(session, uid)
    awards: dict[int, Sequence[tuple[int, str, str]]] = {}
    met_sums: dict[int, int] = {}

    for lid, _, _, _ in levels:
        awards[lid] = await _get_awards(session, lid)
        met_sums[lid] = 0
        if len(awards[lid]) == 0:
            continue
        imgs: list[PILImage] = []
        for aid, _, _ in awards[lid]:
            sto = storages[aid] if aid in storages.keys() else 0
            use = used[aid] if aid in used.keys() else 0
            if sto + use:
                met_sums[lid] += 1

    baseImgs: list[PILImage] = []

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderNameInGroup()

    levelName = res.query[str]("等级名字")
    levelId = None
    if levelName is not None:
        levelId = await get_lid_by_name(session, levelName)

    if levelId is not None:
        baseImgs.append(
            await getTextImage(
                text=f"{name} 的{levelName}进度：",
                color="#FFFFFF",
                font=Fonts.HARMONYOS_SANS_BLACK,
                font_size=80,
                margin_bottom=30,
                width=216 * 8,
            )
        )

    else:
        percent_progress: float = calc_progress(levels, met_sums, awards)
        baseImgs.append(
            await getTextImage(
                text=f"{name} 的抓小哥进度：{str(round(percent_progress*100, 2))}%",
                color="#FFFFFF",
                font=Fonts.HARMONYOS_SANS_BLACK,
                font_size=80,
                margin_bottom=30,
                width=216 * 8,
            )
        )

    for lid, lname, lcolor, lweight in levels:
        if levelId is not None and lid != levelId:
            continue
        if len(awards[lid]) == 0:
            continue
        imgs: list[PILImage] = []
        for aid, name, img in awards[lid]:
            color = lcolor
            sto = storages[aid] if aid in storages.keys() else 0
            use = used[aid] if aid in used.keys() else 0

            if sto + use == 0:
                if lweight == 0:
                    continue
                img = "./res/blank_placeholder.png"
                name = la.disp.award_unknown_name
                color = "#696361"
            elif aid in skins.keys():
                img = skins[aid]

            imgs.append(
                await ref_book_box(name, str(sto) if (sto + use) else "", color, img)
            )

        lAwardCount = len(awards[lid]) if (lweight or met_sums[lid] > 1) else 1
        title = f"{lname} {met_sums[lid]}/{lAwardCount}"

        baseImgs.append(
            await getTextImage(
                text=title,
                color=lcolor,
                font=[Fonts.JINGNAN_JUNJUN, Fonts.MAPLE_UI],
                font_size=80,
                width=216 * 8,
            )
        )

        baseImgs.append(await _combine_cells(imgs))

    img = await verticalPile(baseImgs, 15, "left", "#9B9690", 60, 60, 60, 60)
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))


@listenOnebot()
@matchAlconna(Alconna("re:(kc|抓库存|抓小哥库存)"))
@withLoading(la.loading.kc)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, __: Arparma):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    if uid is None:
        return

    levels = await _get_levels(session)
    skins, storages, used = await _get_others(session, uid)

    imgs: list[PILImage] = []
    for lid, _, lcolor, _ in levels:
        awards = await _get_awards(session, lid)
        _imgs: list[tuple[int, PILImage]] = []

        if len(awards) == 0:
            continue
        for aid, name, img in awards:
            color = lcolor
            sto = storages[aid] if aid in storages.keys() else 0
            use = used[aid] if aid in used.keys() else 0

            if sto == 0:
                continue
            if aid in skins.keys():
                img = skins[aid]

            _imgs.append((sto, await ref_book_box(name, str(sto), color, img)))

        _imgs.sort(key=lambda x: -x[0])
        imgs += [i[1] for i in _imgs]

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderNameInGroup()

    area_title = await getTextImage(
        text=f"{name} 的抓小哥库存：",
        font_size=80,
        font=Fonts.HARMONYOS_SANS_BLACK,
        color="#FFFFFF",
        width=216 * 8,
        margin_bottom=30,
    )
    area_box = await pileImages(images=imgs, rowMaxNumber=8, background="#9B9690")
    img = await verticalPile(
        [area_title, area_box], 15, "left", "#9B9690", 60, 60, 60, 60
    )
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        "re:(所有|全部)小哥",
        ["::"],
        Option(
            "等级",
            Arg("等级名字", str),
            alias=["--level", "级别", "-l", "-L"],
            compact=True,
        ),
    )
)
@withLoading(la.loading.all_xg)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, res: Arparma):
    levels = await _get_levels(session)

    levelName = res.query[str]("等级名字")
    levelId = None
    if levelName is not None:
        levelId = await get_lid_by_name(session, levelName)

    awards: dict[int, Sequence[tuple[int, str, str]]] = {}
    total: int = 0
    for lid, lname, lcolor, _ in levels:
        if levelId is not None and lid != levelId:
            continue
        awards[lid] = await _get_awards(session, lid)
        total += len(awards[lid])

    baseImgs: list[PILImage] = []
    lNameDisplay = f" {levelName} " if levelId is not None else ""
    baseImgs.append(
        await getTextImage(
            text=f"全部 {total} 只{lNameDisplay}小哥：",
            color="#FFFFFF",
            font=Fonts.HARMONYOS_SANS_BLACK,
            font_size=80,
            margin_bottom=30,
            width=216 * 8,
        )
    )

    for lid, lname, lcolor, _ in levels:
        if levelId is not None and lid != levelId:
            continue

        if len(awards[lid]) == 0:
            continue
        imgs: list[PILImage] = []
        for _, name, img in awards[lid]:
            color = lcolor
            imgs.append(await ref_book_box(name, "", color, img))

        title = f"{lname} 共 {len(awards[lid])} 只"

        baseImgs.append(
            await getTextImage(
                text=title,
                color=lcolor,
                font=[Fonts.JINGNAN_JUNJUN, Fonts.MAPLE_UI],
                font_size=80,
                width=216 * 8,
            )
        )

        baseImgs.append(await _combine_cells(imgs))

    img = await verticalPile(baseImgs, 15, "left", "#9B9690", 60, 60, 60, 60)
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))
