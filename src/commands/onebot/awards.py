import math
from typing import Sequence

from interfaces.nonebot.views.catch import render_award_info_message
from src.base.exceptions import DoNotHaveException
from src.common.decorators.command_decorators import kagami_exception_handler
from src.core.unit_of_work import get_unit_of_work
from src.imports import *
from src.logic.admin import isAdmin


@listenPublic()
@kagami_exception_handler()
@matchAlconna(
    Alconna(
        "展示",
        Arg("名字", str),
        Option("皮肤", Arg("皮肤名", str), alias=["--skin", "-s"]),
        Option("管理员", alias=["--admin", "-a"]),
        Option("条目", alias=["--display", "-d"]),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    name = res.query[str]("名字")
    if name is None:
        return
    skin_name = res.query[str]("皮肤名")
    do_admin = res.find("管理员") and isAdmin(ctx)
    do_display = res.find("条目")

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(name)
        sid = None
        uid = await uow.users.get_uid(ctx.sender_id)
        notation = ""

        if not do_admin:
            sto = await uow.inventories.get_storage(uid, aid)
            if sto <= 0:
                raise DoNotHaveException(name)
            notation = str(sto)

        if skin_name is not None:
            sid = await uow.skins.get_sid_strong(skin_name)
            if not do_admin and not await uow.skin_inventory.do_user_have(uid, sid):
                raise DoNotHaveException(skin_name)
            uid = None
        if do_admin:
            uid = None
        info = await uow_get_award_info(uow, aid, uid, sid)
        info.new = False
        info.notation = notation

    if do_display:
        msg = await render_award_info_message(info)
        await ctx.send(msg)
    else:
        msg = (
            UniMessage.text(f"{info.display_name}【{info.level.display_name}】")
            .image(raw=info.image_bytes)
            .text(f"\n{info.description}")
        )
        await ctx.reply(msg)


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


async def _get_levels():
    return [
        (level.lid, level.display_name, level.color, level.weight)
        for level in level_repo.sorted
    ]


async def _get_awards(session: AsyncSession, lid: int):
    query = select(Award.data_id, Award.name, Award.image).filter(Award.level_id == lid)
    return (await session.execute(query)).tuples().all()


async def _get_others(session: AsyncSession, uid: int):
    query = (
        select(Skin.award_id, Skin.image)
        .join(SkinRecord, SkinRecord.skin_id == Skin.data_id)
        .filter(SkinRecord.user_id == uid, SkinRecord.selected == 1)
    )
    skins = (await session.execute(query)).tuples().all()
    skins = dict(skins)

    storages = await InventoryRepository(session).get_inventory_dict(uid)
    return skins, storages


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
            f"{name}: {lweight} ^ {1.0 / param} = {math.pow(lweight, 1.0 / param)}"
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
async def _(ctx: OnebotContext, session: AsyncSession, res: Arparma):
    uid = await get_uid_by_qqid(session, ctx.sender_id)
    if uid is None:
        return

    levels = await _get_levels()
    skins, storages = await _get_others(session, uid)
    awards: dict[int, Sequence[tuple[int, str, str]]] = {}
    met_sums: dict[int, int] = {}

    for lid, _, _, _ in levels:
        awards[lid] = await _get_awards(session, lid)
        met_sums[lid] = 0
        if len(awards[lid]) == 0:
            continue
        imgs: list[PILImage] = []
        for aid, _, _ in awards[lid]:
            sto, use = storages[aid] if aid in storages.keys() else (0, 0)
            if sto + use:
                met_sums[lid] += 1

    baseImgs: list[PILImage] = []

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderName()

    levelName = res.query[str]("等级名字")
    target_level = None
    if levelName is not None:
        target_level = level_repo.get_by_name(levelName)

    if target_level is not None:
        baseImgs.append(
            await getTextImage(
                text=f"{name} 的{target_level.display_name}进度：",
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
        if target_level is not None and lid != target_level.lid:
            continue
        if len(awards[lid]) == 0:
            continue
        imgs: list[PILImage] = []
        for aid, name, img in awards[lid]:
            color = lcolor
            sto, use = storages[aid] if aid in storages.keys() else (0, 0)

            if sto + use == 0:
                if lweight == 0:
                    continue
                img = "./res/blank_placeholder.png"
                name = la.disp.award_unknown_name
                color = "#696361"
            elif aid in skins.keys():
                img = skins[aid]

            imgs.append(
                await ref_book_box(
                    name, str(sto) if (sto + use) else "", str(sto + use), color, img
                )
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
async def _(ctx: OnebotContext, session: AsyncSession, __: Arparma):
    uid = await get_uid_by_qqid(session, ctx.sender_id)
    if uid is None:
        return

    levels = await _get_levels()
    skins, storages = await _get_others(session, uid)

    imgs: list[PILImage] = []
    for lid, _, lcolor, _ in levels:
        awards = await _get_awards(session, lid)
        _imgs: list[tuple[int, PILImage]] = []

        if len(awards) == 0:
            continue
        for aid, name, img in awards:
            color = lcolor
            sto, _ = storages[aid] if aid in storages.keys() else (0, 0)

            if sto == 0:
                continue
            if aid in skins.keys():
                img = skins[aid]

            _imgs.append((sto, await ref_book_box(name, str(sto), "", color, img)))

        _imgs.sort(key=lambda x: -x[0])
        imgs += [i[1] for i in _imgs]

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderName()

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
async def _(ctx: OnebotContext, session: AsyncSession, res: Arparma):
    levels = await _get_levels()

    levelName = res.query[str]("等级名字")
    target_level = None
    if levelName is not None:
        target_level = level_repo.get_by_name(levelName)

    awards: dict[int, Sequence[tuple[int, str, str]]] = {}
    total: int = 0
    for lid, lname, lcolor, _ in levels:
        if target_level is not None and lid != target_level.lid:
            continue
        awards[lid] = await _get_awards(session, lid)
        total += len(awards[lid])

    baseImgs: list[PILImage] = []
    lNameDisplay = f" {levelName} " if target_level is not None else ""
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
        if target_level is not None and lid != target_level.lid:
            continue

        if len(awards[lid]) == 0:
            continue
        imgs: list[PILImage] = []
        for _, name, img in awards[lid]:
            color = lcolor
            imgs.append(await ref_book_box(name, "", "", color, img))

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


@listenGroup()
async def _(ctx: GroupContext):
    """
    赤石
    """

    msg = ctx.message
