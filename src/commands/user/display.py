from typing import Any

from arclet.alconna import Alconna, Arg, Arparma, Option
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import OnebotContext
from src.base.exceptions import DoNotHaveException
from src.common.data.awards import get_award_info
from src.common.decorators.command_decorators import listenOnebot, matchAlconna
from src.core.unit_of_work import get_unit_of_work
from src.logic.admin import isAdmin
from src.ui.pages.catch import render_award_info_message


@listenOnebot()
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
            sto = await uow.inventories.get_stats(uid, aid)
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
        info = await get_award_info(uow, aid, uid, sid)
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
