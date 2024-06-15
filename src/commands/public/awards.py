"""
对小哥进行的增删查改操作
"""

from arclet.alconna import Alconna, Arparma, Arg
from nonebot_plugin_alconna import UniMessage
from sqlalchemy import delete, select

from src.common.db import get_session

from src.common.classes.command_events import PublicContext
from src.common.decorators.command_decorators import listenPublic, requireAdmin, matchAlconna

from src.models import *


@listenPublic()
@requireAdmin()
@matchAlconna(
    Alconna(
        "小哥",
        ["::添加", "::创建"],
        Arg("name", str),
        Arg("level", str),
    )
)
async def _(ctx: PublicContext, res: Arparma):
    name = res.query[str]("name")
    levelName = res.query[str]("level")

    assert name is not None
    assert levelName is not None

    session = get_session()

    async with session.begin():
        _award = (
            await session.execute(select(Award.data_id).filter(Award.name == name))
        ).scalar_one_or_none()

        if _award is None:
            _award = (await session.execute(
                select(Award.data_id).filter(
                    Award.alt_names.any(AwardAltName.name == name)
                )
            )).scalar_one_or_none()

        if _award is not None:
            await ctx.reply(UniMessage(f"名字叫 {name} 的小哥已存在。"))
            return

        level = (
            await session.execute(select(Level.data_id).filter(Level.name == levelName))
        ).scalar_one_or_none()

        if level is None:
            level = (
                await session.execute(
                    select(Level.data_id).filter(
                        Level.alt_names.any(LevelAltName.name == levelName)
                    )
                )
            ).scalar_one_or_none()

        if level is None:
            await ctx.reply(UniMessage(f"等级 {levelName} 不存在。"))
            return

        award = Award(level_id=level, name=name)
        session.add(award)
        await session.commit()

        await ctx.reply(UniMessage(f"成功创建名字叫 {name} 的小哥。"))


@listenPublic()
@requireAdmin()
@matchAlconna(
    Alconna(
        "小哥",
        ["::删除", "::移除"],
        Arg("name", str),
    )
)
async def _(ctx: PublicContext, res: Arparma):
    name = res.query[str]("name")

    assert name is not None

    session = get_session()

    async with session.begin():
        await session.execute(
            delete(Award).filter(Award.name == name)
        )
        await session.execute(
            delete(Award).filter(Award.alt_names.any(
                AwardAltName.name == name
            ))
        )
        await session.commit()
        await ctx.reply(UniMessage(f"成功删除名字叫 {name} 的小哥。"))
