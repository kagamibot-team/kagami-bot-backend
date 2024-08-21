from pathlib import Path

import PIL
import PIL.Image
from arclet.alconna import Alconna, Arg, Arparma
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import MessageContext
from src.base.exceptions import DoNotHaveException
from src.common.command_deco import (
    limited,
    listen_message,
    match_alconna,
    require_awake,
)
from src.core.unit_of_work import get_unit_of_work
from src.ui.base.basics import Fonts, pile, render_text, vertical_pile
from src.ui.base.tools import image_to_bytes
from src.ui.components.awards import ref_book_box_raw


@listen_message()
@match_alconna(Alconna("re:(更换|改变|替换|切换)(小哥)?(皮肤)", Arg("小哥名字", str)))
@limited
@require_awake
async def _(ctx: MessageContext, result: Arparma):
    name = result.query[str]("小哥名字")
    assert name is not None

    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        sid = await uow.skins.get_sid(name)

        if sid is None:
            aid = await uow.awards.get_aid_strong(name)
            sids = await uow.skin_inventory.get_list(uid, aid)
            if len(sids) == 0:
                sid = None
            else:
                using = await uow.skin_inventory.get_using(uid, aid)
                if using not in sids:
                    sid = sids[0]
                elif using == sids[-1]:
                    sid = None
                else:
                    sid = sids[sids.index(using) + 1]
        elif not await uow.skin_inventory.do_user_have(uid, sid):
            name, *_ = await uow.skins.get_info(sid)
            raise DoNotHaveException(f"皮肤 {name}")
        else:
            aid = await uow.skins.get_aid(sid)

        await uow.skin_inventory.use(uid, aid, sid)

        aname = (await uow.awards.get_info(aid)).name
        sname = (await uow.skins.get_info(sid))[0] if sid is not None else "默认"

    await ctx.reply(f"已经将 {aname} 的皮肤切换为 {sname} 了。")


@listen_message()
@match_alconna(Alconna("re:(pfjd|pftj|皮肤图鉴|皮肤进度|皮肤收集进度)"))
async def _(ctx: MessageContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        all_skins = await uow.skins.all()
        infos = await uow.awards.get_info_dict([n[1] for n in all_skins])
        skin_inventory = await uow.skin_inventory.get_list(uid)
        using = await uow.skin_inventory.get_using_list(uid)

    _boxes: list[tuple[str, str, str, str, str]] = []
    _un = (
        "???",
        "",
        "",
        "#696361",
        "./res/blank_placeholder.png",
    )

    name = await ctx.get_sender_name()
    area_title = render_text(
        text=f"{name} 的皮肤进度：",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=80,
        margin_bottom=30,
        width=216 * 6,
    )

    for sid, aid, sname, _, img, _ in all_skins:
        aname = infos[aid].name
        if sid not in skin_inventory:
            _boxes.append(_un)
            continue

        notation = "使用中" if sid in using else ""
        _boxes.append((sname, aname, notation, infos[aid].level.color, img))

    boxes: list[PIL.Image.Image] = []
    for sn, an, no, co, im in _boxes:
        boxes.append(
            ref_book_box_raw(
                color=co,
                image=Path(im),
                new=False,
                notation_bottom=no,
                notation_top="",
                name=sn,
                name_bottom=an,
            )
        )

    area_box = pile(images=boxes, columns=6, background="#9B9690")

    img = vertical_pile([area_title, area_box], 15, "left", "#9B9690", 60, 60, 60, 60)
    await ctx.send(UniMessage().image(raw=image_to_bytes(img)))
