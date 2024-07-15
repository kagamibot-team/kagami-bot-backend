"""
对小哥进行的增删查改操作
"""

from typing import Any

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma, MultiVar, Option
from loguru import logger
from nonebot_plugin_alconna import At, Image, UniMessage
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.command_events import GroupContext, OnebotContext
from src.base.db import get_session
from src.common.data.awards import download_award_image, get_aid_by_name
from src.common.decorators.command_decorators import (
    listenGroup,
    listenOnebot,
    matchAlconna,
    requireAdmin,
    withFreeSession,
)
from src.common.lang.zh import la
from src.core.unit_of_work import get_unit_of_work
from src.models.models import Award, AwardAltName
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
    name = res.query[str]("name")
    levelName = res.query[str]("level")

    assert name is not None
    assert levelName is not None

    async with get_unit_of_work() as uow:
        _award = await uow.awards.get_aid(name)

        if _award is not None:
            await ctx.reply(UniMessage(la.err.award_exists.format(name)))
            return

        level_obj = level_repo.get_by_name(levelName)
        if level_obj is None:
            await ctx.reply(UniMessage(la.err.level_not_found.format(levelName)))
            return

        await uow.awards.add_award(name, level_obj.lid)
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

    session = get_session()

    async with session.begin():
        await session.execute(delete(Award).filter(Award.name == name))
        await session.execute(
            delete(Award).where(
                AwardAltName.award_id == Award.data_id, AwardAltName.name == name
            )
        )
        await session.commit()
        await ctx.reply(UniMessage(la.msg.award_delete_success.format(name)))


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
    )
)
@withFreeSession()
async def _(session: AsyncSession, ctx: OnebotContext, res: Arparma):
    name = res.query[str]("小哥原名")

    if name is None:
        return

    aid = await get_aid_by_name(session, name)

    if aid is None:
        await ctx.reply(UniMessage(la.err.award_not_found.format(name)))
        return

    newName = res.query[str]("小哥新名字")
    levelName = res.query[str]("等级名字")
    _description = res.query[tuple[str]]("描述")
    image = res.query[Image]("图片")
    special = res.query[str]("特殊性")

    messages = UniMessage() + "本次更改结果：\n\n"

    if newName is not None:
        await session.execute(
            update(Award).where(Award.data_id == aid).values(name=newName)
        )
        messages += f"成功将名字叫 {name} 的小哥的名字改为 {newName}。\n"

    if levelName is not None:
        level = level_repo.get_by_name(levelName)

        if level is None:
            messages += f"更改等级未成功，因为名字叫 {levelName} 的等级不存在。"
        else:
            await session.execute(
                update(Award).where(Award.data_id == aid).values(level_id=level.lid)
            )
            messages += f"成功将名字叫 {name} 的小哥的等级改为 {levelName}。\n"

    if _description is not None:
        description = "\n".join(_description)
        await session.execute(
            update(Award).where(Award.data_id == aid).values(description=description)
        )
        messages += f"成功将名字叫 {name} 的小哥的描述改为 {description}\n"

    if image is not None:
        imageUrl = image.url
        if imageUrl is None:
            logger.warning(f"名字叫 {name} 的小哥的图片地址为空。")
        else:
            try:
                fp = await download_award_image(aid, imageUrl)
                await session.execute(
                    update(Award).where(Award.data_id == aid).values(image=fp)
                )
                messages += f"成功将名字叫 {name} 的小哥的图片改为 {fp}。\n"
            except Exception as e:  # pylint: disable=broad-except
                logger.warning(f"名字叫 {name} 的小哥的图片下载失败。")
                logger.exception(e)

    if special is not None and len(special) > 0:
        if special[0] in "yYtT":
            await session.execute(
                update(Award)
                .where(Award.data_id == aid)
                .values(is_special_get_only=True)
            )
            messages += f"成功将名字叫 {name} 的小哥更改为抽不到，不能被随机合成出来\n"
        elif special[0] in "nNfF":
            await session.execute(
                update(Award)
                .where(Award.data_id == aid)
                .values(is_special_get_only=False)
            )
            messages += f"成功将名字叫 {name} 的小哥更改为抽得到，可以被随机合成出来\n"

    await ctx.reply(messages)


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
