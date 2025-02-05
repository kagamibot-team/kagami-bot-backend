from typing import Any

from arclet.alconna import Alconna, Arg, Arparma, Option
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import MessageContext
from src.base.exceptions import DoNotHaveException, KagamiArgumentException
from src.base.message import image, text
from src.common.command_deco import listen_message, match_alconna
from src.common.data.awards import get_award_info
from src.core.unit_of_work import get_unit_of_work
from src.logic.admin import is_admin
from src.services.stats import StatService
from src.ui.pages.catch import render_award_info_message
from src.ui.views.award import AwardDisplay


@listen_message()
@match_alconna(
    Alconna(
        "展示",
        Arg("名字", str),
        Option("皮肤", Arg("皮肤名", str), alias=["--skin", "-s"]),
        Option("管理员", alias=["--admin", "-a"]),
        Option("条目", alias=["--display", "-d"]),
    )
)
async def _(ctx: MessageContext, res: Arparma[Any]):
    name = res.query[str]("名字")
    if name is None:
        return
    skin_name = res.query[str]("皮肤名")
    do_admin = res.find("管理员") and is_admin(ctx)
    do_display = res.find("条目")

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(name)
        sid = None
        uid = await uow.users.get_uid(ctx.sender_id)
        sto: int | None = None
        sta: int | None = None

        if not do_admin:
            sto = await uow.inventories.get_storage(uid, aid)
            sta = await uow.inventories.get_stats(uid, aid)
            if sta <= 0:
                raise DoNotHaveException(name)

        if skin_name is not None:
            sid = await uow.skins.get_sid_strong(skin_name)
            if not do_admin and not await uow.skin_inventory.do_user_have(uid, sid):
                raise DoNotHaveException(skin_name)
            if await uow.skins.get_aid(sid) != aid:
                raise KagamiArgumentException("这个皮肤不是这个小哥的！")
            uid = None
        if do_admin:
            uid = None
        info = await get_award_info(uow, aid, uid, sid)

        main_pack = await uow.pack.get_main_pack(aid)
        linked_pack = await uow.pack.get_linked_packs(aid)
        dt = AwardDisplay(info=info)

        await StatService(uow).display(uid, aid, sid)

    if do_display:
        msg = await render_award_info_message(dt, count=sto, stats=sta)
        await ctx.send(msg)
    elif do_admin:
        await ctx.reply(
            text(f"{info.display_name}【{info.level.display_name}】")
            + image(info.image_resource.path)
            + text(
                f"id={aid};\n"
                f"main_pack={main_pack}; linked={linked_pack};\n"
                f"sid={info.sid}; slevel={info.slevel};\n"
                f"{info.description}"
            )
        )
    else:
        await ctx.reply(
            text(f"{info.display_name}【{info.level.display_name}】")
            + image(info.image_resource.path)
            + text(f"\n{info.description}")
        )
