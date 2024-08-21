from pathlib import Path

import PIL
import PIL.Image
from arclet.alconna import Alconna, Arg, ArgFlag, Arparma, MultiVar, Option
from loguru import logger
from nonebot_plugin_alconna import Image, UniMessage
from sqlalchemy import select, update

from src.base.command_events import MessageContext
from src.base.exceptions import ObjectAlreadyExistsException
from src.common.command_deco import listen_message, match_alconna, require_admin
from src.common.data.skins import downloadSkinImage
from src.core.unit_of_work import get_unit_of_work
from src.models.level import level_repo
from src.models.models import Award, AwardAltName, Skin, SkinAltName
from src.ui.base.basics import Fonts, pile, render_text, vertical_pile
from src.ui.base.tools import image_to_bytes
from src.ui.components.awards import ref_book_box_raw


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(所有|全部)皮肤",
        Arg("name", str, flags=[ArgFlag.OPTIONAL]),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("name")

    async with get_unit_of_work() as uow:
        session = uow.session
        query = select(
            Skin.name, Award.name, Skin.price, Award.level_id, Skin.image
        ).join(Award, Skin.award_id == Award.data_id)

        if name:
            query1 = query.filter(Award.name == name)
            query2 = query.filter(Skin.name == name)
            query3 = query.join(
                AwardAltName, AwardAltName.award_id == Award.data_id
            ).filter(AwardAltName.name == name)
            query4 = query.join(
                SkinAltName, SkinAltName.skin_id == Skin.data_id
            ).filter(SkinAltName.name == name)

            skins1 = (await session.execute(query1)).tuples()
            skins2 = (await session.execute(query2)).tuples()
            skins3 = (await session.execute(query3)).tuples()
            skins4 = (await session.execute(query4)).tuples()

            skins = list(skins1) + list(skins2) + list(skins3) + list(skins4)
        else:
            skins = list((await session.execute(query)).tuples())

        skins = sorted(skins, key=lambda s: level_repo.sorted_index[s[3]])

    boxes: list[PIL.Image.Image] = []
    for sn, an, pr, lid, im in skins:
        boxes.append(
            ref_book_box_raw(
                color=uow.levels[lid].color,
                image=Path(im),
                new=False,
                notation_bottom=str(pr),
                notation_top="",
                name=sn,
                name_bottom=an,
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

    img = vertical_pile([area_title, area_box], 15, "left", "#9B9690", 60, 60, 60, 60)
    await ctx.send(UniMessage().image(raw=image_to_bytes(img)))


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
        await uow.skins.add_skin(aid, sname)

    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
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
        Option("图片", Arg("图片", Image), alias=["--image", "照片", "-i", "-I"]),
        Option(
            "价格", Arg("价格", float), alias=["--price", "价钱", "售价", "-p", "-P"]
        ),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("皮肤原名")
    assert name is not None
    newName = res.query[str]("皮肤新名字")
    price = res.query[float]("价格")
    _description = res.query[tuple[str]]("描述")
    image = res.query[Image]("图片")

    async with get_unit_of_work() as uow:
        sid = await uow.skins.get_sid_strong(name)
        session = uow.session

        if newName is not None:
            await session.execute(
                update(Skin).where(Skin.data_id == sid).values({Skin.name: newName})
            )

        if price is not None:
            await session.execute(
                update(Skin).where(Skin.data_id == sid).values({Skin.price: price})
            )

        if _description is not None:
            description = "\n".join(_description)
            await session.execute(
                update(Skin)
                .where(Skin.data_id == sid)
                .values({Skin.description: description})
            )

        if image is not None:
            imageUrl = image.url
            if imageUrl is None:
                logger.warning(f"名字叫 {name} 的皮肤的图片地址为空。")
            else:
                fp = await downloadSkinImage(sid, imageUrl)
                await session.execute(
                    update(Skin).where(Skin.data_id == sid).values({Skin.image: fp})
                )

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
