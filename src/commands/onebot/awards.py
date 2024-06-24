import pathlib
import math

from src.imports import *
from typing import Sequence


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


async def _combine_cells(imgs: list[PILImage], marginTop: int = 0):
    return await combineABunchOfImage(
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


async def _title(lname: str, lcolor: str):
    return await drawABoxOfText(
        f"{lname}",
        lcolor,
        textFont(Fonts.HARMONYOS_SANS_BLACK, 60),
        background="#9B9690",
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
@matchAlconna(Alconna("re:(zhuajd|抓进度|抓小哥进度)"))
@withLoading(la.loading.zhuajd)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, __: Arparma):
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

    percent_progress: float = calc_progress(levels, met_sums, awards)
    baseImgs.append(
        await drawASingleLineClassic(
            f"{name} 的抓小哥进度：{str(round(percent_progress*100, 2))}%",
            "#FFFFFF",
            Fonts.HARMONYOS_SANS_BLACK,
            80,
            0,
            30,
        )
    )

    for lid, lname, lcolor, lweight in levels:
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

        baseImgs.append(
            await _title(f"{lname} {met_sums[lid]}/{len(awards[lid])}", lcolor)
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

            if sto + use == 0:
                continue
            if aid in skins.keys():
                img = skins[aid]

            _imgs.append((sto, await ref_book_box(name, str(sto), color, img)))

        _imgs.sort(key=lambda x: -x[0])
        imgs += [i[1] for i in _imgs]

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderNameInGroup()

    area_title = await drawASingleLineClassic(
        f"{name} 的抓小哥库存：", "#FFFFFF", Fonts.HARMONYOS_SANS_BLACK, 80, 0, 30
    )
    area_box = await combineABunchOfImage(
        paddingX=0,
        paddingY=0,
        images=imgs,
        rowMaxNumber=8,
        background="#9B9690",
        horizontalAlign="top",
        verticalAlign="left",
    )
    img = await verticalPile(
        [area_title, area_box], 15, "left", "#9B9690", 60, 60, 60, 60
    )
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna("re:(所有|全部)小哥", ["::"]))
@withLoading(la.loading.all_xg)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, __: Arparma):
    levels = await _get_levels(session)

    baseImgs: list[PILImage] = []
    for lid, lname, lcolor, _ in levels:
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
