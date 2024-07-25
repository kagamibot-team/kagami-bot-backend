import PIL
import PIL.Image
from arclet.alconna import Alconna, Arg, ArgFlag, Arparma
from nonebot_plugin_alconna import UniMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.command_events import GroupContext, OnebotContext
from src.common.data.awards import get_aid_by_name
from src.common.data.skins import (
    do_user_have_skin,
    get_sid_by_name,
    get_skin_name,
    switch_skin_of_award,
    use_skin,
)
from src.common.data.users import get_uid_by_qqid
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
    withFreeSession,
    withLoading,
    withSessionLock,
)
from src.common.lang.zh import la
from src.models.models import Award, AwardAltName, Skin, SkinAltName, SkinRecord
from src.models.statics import level_repo
from src.ui.base.basics import Fonts, pile, render_text, vertical_pile
from src.ui.base.tools import image_to_bytes
from src.ui.deprecated.ref_book import skin_book


@listenOnebot()
@matchAlconna(Alconna("re:(更换|改变|替换|切换)(小哥)?(皮肤)", Arg("name", str)))
@withSessionLock()
async def _(
    ctx: OnebotContext,
    session: AsyncSession,
    result: Arparma,
):
    name = result.query[str]("name")
    user = await get_uid_by_qqid(session, ctx.sender_id)

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
        await ctx.reply(
            UniMessage().text(
                la.msg.skin_set_2.format(name, await get_skin_name(session, skin))
            )
        )

    await session.commit()


@listenOnebot()
@matchAlconna(Alconna("re:(pfjd|pftj|皮肤图鉴|皮肤进度|皮肤收集进度)"))
@withLoading()
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, _: Arparma):
    uid = await get_uid_by_qqid(session, ctx.sender_id)

    query = select(
        Skin.data_id, Skin.image, Skin.name, Award.name, Award.level_id
    ).join(Award, Award.data_id == Skin.award_id)
    skins = (await session.execute(query)).tuples().all()
    skins = sorted(skins, key=lambda s: level_repo.sorted_index[s[4]])

    query = select(SkinRecord.skin_id, SkinRecord.selected).filter(
        SkinRecord.user_id == uid
    )
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
        name = await ctx.getSenderName()

    area_title = render_text(
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

    boxes: list[PIL.Image.Image] = []
    for box in _boxes:
        boxes.append(await skin_book(*box))

    area_box = pile(images=boxes, columns=6, background="#9B9690")

    img = vertical_pile(
        [area_title, area_box], 15, "left", "#9B9690", 60, 60, 60, 60
    )
    await ctx.send(UniMessage().image(raw=image_to_bytes(img)))


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
async def _(session: AsyncSession, ctx: OnebotContext, res: Arparma):
    name = res.query[str]("name")

    query = select(Skin.name, Award.name, Skin.price, Award.level_id, Skin.image).join(
        Award, Skin.award_id == Award.data_id
    )

    if name:
        query1 = query.filter(Award.name == name)
        query2 = query.filter(Skin.name == name)
        query3 = query.join(
            AwardAltName, AwardAltName.award_id == Award.data_id
        ).filter(AwardAltName.name == name)
        query4 = query.join(SkinAltName, SkinAltName.skin_id == Skin.data_id).filter(
            SkinAltName.name == name
        )

        skins1 = (await session.execute(query1)).tuples()
        skins2 = (await session.execute(query2)).tuples()
        skins3 = (await session.execute(query3)).tuples()
        skins4 = (await session.execute(query4)).tuples()

        skins = list(skins1) + list(skins2) + list(skins3) + list(skins4)
    else:
        skins = list((await session.execute(query)).tuples())

    skins = sorted(skins, key=lambda s: level_repo.sorted_index[s[3]])

    boxes: list[PIL.Image.Image] = []
    for box in skins:
        boxes.append(
            await skin_book(
                box[0], box[1], str(box[2]), level_repo.levels[box[3]].color, box[4]
            )
        )

    area_title = render_text(
        text=f"全部 {len(skins)} 种皮肤：",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=80,
        margin_bottom=30,
        width=216 * 6,
    )

    area_box = pile(images=boxes, columns=6, background="#9B9690")

    img = vertical_pile(
        [area_title, area_box], 15, "left", "#9B9690", 60, 60, 60, 60
    )
    await ctx.send(UniMessage().image(raw=image_to_bytes(img)))
