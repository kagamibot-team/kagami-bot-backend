from arclet.alconna import Alconna, Arg, Arparma, MultiVar, Option
from loguru import logger
from nonebot_plugin_alconna import Image
from sqlalchemy import update

from src.base.command_events import OnebotContext
from src.base.exceptions import ObjectAlreadyExistsException
from src.common.data.skins import downloadSkinImage
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
)
from src.core.unit_of_work import get_unit_of_work
from src.models.models import Skin


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "re:(创建|新增|增加|添加)皮肤",
        Arg("小哥名", str),
        Arg("皮肤名", str),
    )
)
async def _(ctx: OnebotContext, res: Arparma):
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


@listenOnebot()
@requireAdmin()
@matchAlconna(
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
async def _(ctx: OnebotContext, res: Arparma):
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
                update(Skin).where(Skin.data_id == sid).values(name=newName)
            )

        if price is not None:
            await session.execute(
                update(Skin).where(Skin.data_id == sid).values(price=price)
            )

        if _description is not None:
            description = "\n".join(_description)
            await session.execute(
                update(Skin)
                .where(Skin.data_id == sid)
                .values(extra_description=description)
            )

        if image is not None:
            imageUrl = image.url
            if imageUrl is None:
                logger.warning(f"名字叫 {name} 的皮肤的图片地址为空。")
            else:
                fp = await downloadSkinImage(sid, imageUrl)
                await session.execute(
                    update(Skin).where(Skin.data_id == sid).values(image=fp)
                )

    await ctx.send("ok.")
