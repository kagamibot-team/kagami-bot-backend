from arclet.alconna import Alconna, Arg, Arparma, MultiVar, Option
from nonebot_plugin_alconna import Image

from src.base.command_events import MessageContext
from src.base.exceptions import ObjectAlreadyExistsException, ObjectNotFoundException
from src.common.command_deco import (
    listen_message,
    match_alconna,
    match_literal,
    require_admin,
)
from src.common.data.awards import download_award_image
from src.core.unit_of_work import get_unit_of_work
from src.models.level import level_repo
from src.services.pool import PoolService


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "小哥",
        ["::添加", "::创建"],
        Arg("name", str),
        Arg("level", str),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    aname = res.query[str]("name")
    lname = res.query[str]("level")
    assert aname is not None
    assert lname is not None

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid(aname)
        if aid is not None:
            raise ObjectAlreadyExistsException(aname)
        level_obj = level_repo.get_by_name(lname)
        if level_obj is None:
            raise ObjectNotFoundException("等级")
        await uow.awards.add_award(aname, level_obj.lid)
    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "小哥",
        ["::删除", "::移除"],
        Arg("name", str),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("name")
    assert name is not None

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(name)
        await uow.awards.delete_award(aid)
    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "re:(修改|更改|调整|改变|设置|设定)小哥",
        ["::"],
        Arg("小哥原名", str),
        Option(
            "名字",
            Arg("小哥新名字", str),
            alias=["--name", "名称", "-n", "-N"],
            compact=True,
        ),
        Option(
            "等级",
            Arg("等级名字", str),
            alias=["--level", "级别", "-l", "-L"],
            compact=True,
        ),
        Option(
            "描述",
            Arg("描述", MultiVar(str, flag="+"), seps="\n"),
            alias=["--description", "-d", "-D"],
            compact=True,
        ),
        Option("图片", Arg("图片", Image), alias=["--image", "照片", "-i", "-I"]),
        Option("猎场", Arg("猎场", int), alias=["--packs", "所在猎场"]),
        Option(
            "排序优先度",
            Arg("排序优先度", int),
            alias=["--priority", "优先度", "-p", "-P"],
        ),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("小哥原名")
    newName = res.query[str]("小哥新名字")
    levelName = res.query[str]("等级名字")
    _description = res.query[tuple[str]]("描述") or ()
    image = res.query[Image]("图片")
    pack_id = res.query[int]("猎场")
    sorting = res.query[int]("排序优先度")

    assert name is not None

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(name)
        lid = (
            uow.levels.get_by_name_strong(levelName).lid
            if levelName is not None
            else None
        )
        image = image.url if image is not None else None
        image = await download_award_image(aid, image) if image is not None else None
        await uow.awards.modify(
            aid=aid,
            name=newName,
            description="".join(_description),
            lid=lid,
            image=image,
            pack_id=pack_id,
            sorting=sorting,
        )

    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_literal("::抓不到的小哥")
async def _(ctx: MessageContext):
    async with get_unit_of_work() as uow:
        service = PoolService(uow)
        list = await service.get_uncatchable_aids()
    await ctx.reply(str(list))
