from typing import Any

from arclet.alconna import Alconna, Arg, Arparma, Option
from nonebot_plugin_alconna import UniMessage

from src.ui.pages.catch import render_award_info_message
from src.ui.pages.storage import (
    render_progress_message,
    render_storage_message,
)
from src.base.command_events import OnebotContext
from src.base.exceptions import DoNotHaveException
from src.common.data.awards import get_a_list_of_award_info, get_award_info
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
    withLoading,
)
from src.common.lang.zh import la
from src.core.unit_of_work import UnitOfWork, get_unit_of_work
from src.logic.admin import isAdmin
from src.ui.views.list_view import UserStorageView
from src.ui.views.user import UserData


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


async def get_storage_view(
    uow: UnitOfWork,
    userdata: UserData | None,
    level_name: str | None,
    show_notation2: bool = True,
) -> UserStorageView:
    uid = None if userdata is None else userdata.uid
    view = UserStorageView(user=userdata)
    if level_name is not None:
        view.limited_level = uow.levels.get_by_name_strong(level_name)

    for level in uow.levels.sorted:
        if level_name is not None and level != view.limited_level:
            continue
        aids = await uow.awards.get_aids(level.lid)
        infos = await get_a_list_of_award_info(
            uow, uid, aids, show_notation2=show_notation2
        )
        view.awards.append((level, infos))
    return view


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
async def _(ctx: OnebotContext, res: Arparma):
    levelName = res.query[str]("等级名字")
    async with get_unit_of_work(ctx.sender_id) as uow:
        view = await get_storage_view(
            uow,
            UserData(
                uid=await uow.users.get_uid(ctx.sender_id),
                name=await ctx.sender_name,
                qqid=str(ctx.sender_id),
            ),
            levelName,
        )

    await ctx.send(await render_progress_message(view))


@listenOnebot()
@matchAlconna(Alconna("re:(kc|抓库存|抓小哥库存)"))
@withLoading(la.loading.kc)
async def _(ctx: OnebotContext, _: Arparma):
    async with get_unit_of_work(ctx.sender_id) as uow:
        view = await get_storage_view(
            uow,
            UserData(
                uid=await uow.users.get_uid(ctx.sender_id),
                name=await ctx.sender_name,
                qqid=str(ctx.sender_id),
            ),
            None,
            show_notation2=False,
        )

    await ctx.send(await render_storage_message(view))


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
async def _(ctx: OnebotContext, res: Arparma):
    levelName = res.query[str]("等级名字")
    async with get_unit_of_work(ctx.sender_id) as uow:
        view = await get_storage_view(uow, None, levelName)
    await ctx.send(await render_progress_message(view))
