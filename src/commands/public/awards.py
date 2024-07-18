"""
对小哥进行的增删查改操作
"""

from typing import Any

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma, MultiVar, Option
from nonebot_plugin_alconna import At, Image

from src.base.command_events import GroupContext, OnebotContext
from src.base.exceptions import ObjectAlreadyExistsException, ObjectNotFoundException
from src.common.data.awards import download_award_image
from src.common.decorators.command_decorators import (
    listenGroup,
    listenOnebot,
    matchAlconna,
    requireAdmin,
)
from src.core.unit_of_work import get_unit_of_work
from src.models.statics import level_repo


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        "小哥",
        ["::添加", "::创建"],
        Arg("name", str),
        Arg("level", str),
    )
)
async def _(ctx: OnebotContext, res: Arparma):
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
            raise ObjectNotFoundException("等级", lname)
        await uow.awards.add_award(aname, level_obj.lid)
    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        "小哥",
        ["::删除", "::移除"],
        Arg("name", str),
    )
)
async def _(ctx: OnebotContext, res: Arparma):
    name = res.query[str]("name")
    assert name is not None

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(name)
        await uow.awards.delete_award(aid)
    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(
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
        Option(
            "特殊性",
            Arg("特殊性", str),
            alias=["--special", "特殊", "-s", "-S", "是否特殊"],
        ),
        Option(
            "排序优先度",
            Arg("排序优先度", int),
            alias=["--priority", "优先度", "-p", "-P"],
        ),
    )
)
async def _(ctx: OnebotContext, res: Arparma):
    name = res.query[str]("小哥原名")
    newName = res.query[str]("小哥新名字")
    levelName = res.query[str]("等级名字")
    _description = res.query[tuple[str]]("描述") or ()
    image = res.query[Image]("图片")
    special = res.query[str]("特殊性")
    sorting = res.query[int]("排序优先度")
    if name is None:
        return

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(name)
        lid = (
            uow.levels.get_by_name_strong(levelName).lid
            if levelName is not None
            else None
        )
        special = special in ("是", "1", "true", "t", "y", "yes")
        image = image.url if image is not None else None
        image = await download_award_image(aid, image) if image is not None else None
        await uow.awards.modify(
            aid=aid,
            name=newName,
            description="".join(_description),
            lid=lid,
            image=image,
            special=special,
            sorting=sorting,
        )

    await ctx.reply("ok.")


@listenGroup()
@requireAdmin()
@matchAlconna(Alconna(["::"], "给薯片", Arg("对方", int | At), Arg("数量", int)))
async def _(ctx: GroupContext, res: Arparma[Any]):
    target = res.query("对方")
    number = res.query[int]("数量")
    if target is None or number is None:
        return
    if isinstance(target, At):
        target = int(target.target)
    assert isinstance(target, int)

    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(target)
        await uow.users.add_money(uid, number)

    await ctx.reply("给了。", at=False, ref=True)


@listenGroup()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "给小哥",
        Arg("对方", int | At),
        Arg("名称", str),
        Arg("数量", int, flags=[ArgFlag.OPTIONAL]),
    )
)
async def _(ctx: GroupContext, res: Arparma[Any]):
    target = res.query("对方")
    name = res.query[str]("名称")
    number = res.query[int]("数量")
    if target is None or name is None:
        return
    if isinstance(target, At):
        target = int(target.target)
    assert isinstance(target, int)

    if number is None:
        number = 1

    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(target)
        aid = await uow.awards.get_aid_strong(name)
        await uow.inventories.give(uid, aid, number, False)

    await ctx.reply("给了。", at=False, ref=True)
