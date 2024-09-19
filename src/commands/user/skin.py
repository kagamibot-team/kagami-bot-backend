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
from src.common.data.user import get_user_data
from src.core.unit_of_work import get_unit_of_work
from src.services.stats import StatService
from src.ui.base.render import get_render_pool
from src.ui.types.inventory import BookBoxData, BoxItemList, DisplayBoxData, StorageData


@listen_message()
@limited
@match_alconna(Alconna("re:(更换|改变|替换|切换)(小哥)?(皮肤)", Arg("小哥名字", str)))
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
        await StatService(uow).switch_skin(uid, aid, sid)

    await ctx.reply(f"已经将 {aname} 的皮肤切换为 {sname} 了。")


@listen_message()
@match_alconna(Alconna("re:(pfjd|pftj|皮肤图鉴|皮肤进度|皮肤收集进度)"))
async def _(ctx: MessageContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        user = await get_user_data(ctx, uow)
        all_skins = await uow.skins.all()
        infos = await uow.awards.get_info_dict([n[1] for n in all_skins])
        skin_inventory = await uow.skin_inventory.get_list(uid)
        using = await uow.skin_inventory.get_using_list(uid)

        boxes: list[BookBoxData] = []

        unknown_box = BookBoxData(
            display_box=DisplayBoxData(
                image="./resource/blank_placeholder.png",
                color="#696361",
            ),
            title1="???",
        )

        for sid, aid, sname, _, _, _ in all_skins:
            if sid not in skin_inventory:
                boxes.append(unknown_box)
                continue
            info = infos[aid]
            await uow.skins.link(sid, info)
            boxes.append(
                BookBoxData(
                    display_box=DisplayBoxData(
                        image=info.image_url,
                        color=info.color,
                        notation_down="使用中" if sid in using else "",
                    ),
                    title1=sname,
                    title2=info.name,
                )
            )

    data = StorageData(
        user=user,
        title_text="皮肤进度",
        boxes=[
            BoxItemList(
                elements=boxes,
            )
        ],
    )

    await ctx.send(
        UniMessage().image(raw=(await get_render_pool().render("storage", data)))
    )
