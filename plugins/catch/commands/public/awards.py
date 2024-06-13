"""
对小哥进行的增删查改操作
"""

from arclet.alconna import Alconna, Arparma, Arg
from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_orm import get_session

from ...models import *

from ...events.context import PublicContext
from ...events import EventManager
from ..basics.decorator import listenPublic, requireAdmin, matchAlconna


awardManager = EventManager()


@listenPublic(awardManager)
@requireAdmin()
@matchAlconna(Alconna(
    "小哥",
    ["::添加", "::创建"],
    Arg("name", str),
    Arg("level", str),
))
async def addAward(ctx: PublicContext, res: Arparma):
    name = res.query[str]("name")
    levelName = res.query[str]("level")

    assert name is not None
    assert levelName is not None

    session = get_session()

    async with session.begin():
        _award = await getAwardByName(session, name)

        if _award is not None:
            await ctx.reply(UniMessage(f"名字叫 {name} 的小哥已存在。"))
            return
        
        level = await getLevelByName(session, levelName)

        if level is None:
            await ctx.reply(UniMessage(f"等级 {levelName} 不存在。"))
            return

        award = Award(level=level, name=name)
        session.add(award)
        await session.commit()
        
        await ctx.reply(UniMessage(f"成功创建名字叫 {name} 的小哥。"))
