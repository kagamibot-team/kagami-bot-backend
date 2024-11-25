from arclet.alconna import Alconna, Arg, Arparma, MultiVar, Option
from loguru import logger
from nonebot_plugin_alconna import Image, UniMessage
from sqlalchemy import update

from src.base.command_events import MessageContext
from src.base.exceptions import ObjectAlreadyExistsException
from src.common.command_deco import listen_message, match_alconna, require_admin
from src.common.data.skins import download_skin_image
from src.core.unit_of_work import get_unit_of_work
from src.models.models import Skin
from src.ui.base.render import get_render_pool
from src.ui.types.common import UserData
from src.ui.types.inventory import BookBoxData, BoxItemList, DisplayBoxData, StorageData


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(所有|全部)皮肤",
    )
)
async def _(ctx: MessageContext, res: Arparma):
    async with get_unit_of_work(ctx.sender_id) as uow:
        sids = await uow.skins.all_sid()
        sinfos = {sid: await uow.skins.get_info_v2(sid) for sid in sids}
        ainfos = await uow.awards.get_info_dict(
            set(sinfo.aid for sinfo in sinfos.values())
        )

        boxes: list[BookBoxData] = []

        for sid in sids:
            sinfo = sinfos[sid]
            ainfo = sinfo.link(ainfos[sinfo.aid])

            boxes.append(
                BookBoxData(
                    display_box=DisplayBoxData(
                        image=ainfo.image_url,
                        color=ainfo.color,
                    ),
                    title1=sinfo.name,
                    title2=ainfo.name,
                )
            )

    data = StorageData(
        user=UserData(),
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


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(创建|新增|增加|添加)皮肤",
        Arg("小哥名", str),
        Arg("皮肤名", str),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    aname = res.query[str]("小哥名")
    sname = res.query[str]("皮肤名")
    if aname is None or sname is None:
        return

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(aname)
        sid = await uow.skins.get_sid(sname)
        if sid is not None:
            raise ObjectAlreadyExistsException(f"皮肤 {sname}")
        await uow.skins.create_skin(aid, sname)

    await ctx.reply("ok.")


MODIFY_SKIN_ALCONNA = Alconna(
    "re:(修改|更改|调整|改变|设置|设定)皮肤",
    ["::"],
    Arg("皮肤原名", str),
    Option(
        "名字",
        Arg("皮肤新名字", str),
        alias=["--name", "名称", "-n", "-N"],
        compact=True,
    ),
    Option(
        "描述",
        Arg("描述", MultiVar(str, flag="*"), seps="\n"),
        alias=["--description", "-d", "-D"],
        compact=True,
    ),
    Option(
        "图片",
        Arg("图片", Image),
        alias=["--image", "照片", "-i", "-I"],
    ),
    Option(
        "价格",
        Arg("价格", float),
        alias=["--price", "价钱", "售价", "-p", "-P"],
    ),
    Option(
        "饼干价格",
        Arg("饼干价格", int),
        alias=["--biscuit", "-b", "-B", "饼干"],
    ),
    Option(
        "等级",
        Arg("等级", int),
        alias=["--level", "-l", "-L"],
    ),
)


@listen_message()
@require_admin()
@match_alconna(MODIFY_SKIN_ALCONNA)
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("皮肤原名")
    assert name is not None

    new_name = res.query[str]("皮肤新名字")
    price = res.query[float]("价格")
    description_tuple = res.query[tuple[str]]("描述")
    image = res.query[Image]("图片")
    biscuit = res.query[int]("饼干价格")
    level = res.query[int]("等级")

    async with get_unit_of_work() as uow:
        sid = await uow.skins.get_sid_strong(name)
        info = await uow.skins.get_info_v2(sid)

        if new_name is not None:
            info.name = new_name

        if price is not None:
            info.deprecated_price = price

        if description_tuple is not None:
            description = "\n".join(description_tuple)
            info.description = description

        if biscuit is not None:
            info.biscuit_price = biscuit

        if level is not None:
            info.level = level
            
        await uow.skins.set_info_v2(sid, info)

        if image is not None:
            imageUrl = image.url
            if imageUrl is None:
                logger.warning(f"名字叫 {name} 的皮肤的图片地址为空。")
            else:
                await download_skin_image(sid, imageUrl)
    await ctx.send("ok.")


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "re:(删除|移除|移除|删除)皮肤",
        ["::"],
        Arg("皮肤原名", str),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("皮肤原名")
    assert name is not None
    async with get_unit_of_work() as uow:
        sid = await uow.skins.get_sid_strong(name)
        await uow.skins.delete(sid)
    await ctx.send("ok.")
