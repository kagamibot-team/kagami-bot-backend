from functools import reduce
from arclet.alconna import Alconna, Arg, Arparma, MultiVar, Option
from loguru import logger
from nonebot_plugin_alconna import Image, UniMessage

from src.base.command_events import MessageContext
from src.base.exceptions import ObjectAlreadyExistsException
from src.common.command_deco import (
    listen_message,
    match_alconna,
    match_literal,
    require_admin,
)
from src.common.data.skins import download_skin_image
from src.core.unit_of_work import get_unit_of_work
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

        sids = sorted(
            sids,
            key=lambda sid: (
                -sinfos[sid].level,
                -ainfos[sinfos[sid].aid].level.lid,
                sinfos[sid].aid,
            ),
        )

        boxes: list[BookBoxData] = []

        for sid in sids:
            sinfo = sinfos[sid]
            ainfo = sinfo.link(ainfos[sinfo.aid])

            flower_attribute = "✿ " if not sinfo.can_draw else ""

            boxes.append(
                BookBoxData(
                    display_box=DisplayBoxData(
                        image=ainfo.image_url,
                        color=ainfo.color,
                        do_glow=not sinfo.can_draw,
                        new_overlay=sinfo.level == 0,
                    ),
                    title1=flower_attribute + sinfo.name,
                    title2=(
                        f"{ainfo.name}\n\n"
                        f"可抽={sinfo.can_draw}\n"
                        f"可买={sinfo.can_buy}\n"
                        f"薯片={sinfo.deprecated_price}\n"
                        f"饼干={sinfo.biscuit_price}"
                    ),
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
    Option(
        "可被抽",
        Arg("可被抽", bool),
        alias=["--can-draw", "--cd", "--CD"],
    ),
    Option(
        "可被购买",
        Arg("可被购买", bool),
        alias=[
            "--can-buy",
            "--cb",
            "--CB",
            "可被买",
            "可买",
            "上架",
            "可以买",
            "可以购买",
        ],
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
    can_draw = res.query[bool]("可被抽")
    can_buy = res.query[bool]("可被购买")

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

        if can_draw is not None:
            info.can_draw = can_draw

        if can_buy is not None:
            info.can_buy = can_buy

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


@listen_message()
@require_admin()
@match_literal("::skin-no-level")
async def _(ctx: MessageContext):
    async with get_unit_of_work() as uow:
        sids = await uow.skins.get_all_sid_grouped_with_level(True)
        sids = reduce(
            lambda x, y: x | y, (v for i, v in sids.items() if i < 1 or i > 4)
        )
        names = [(await uow.skins.get_info_v2(sid)).name for sid in sids]
    
    await ctx.send(f"No Level: {names}")
