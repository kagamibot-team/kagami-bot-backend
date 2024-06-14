import pathlib
from nonebot_plugin_alconna import Alconna, Arparma, UniMessage
from arclet.alconna import Arg
from nonebot_plugin_orm import AsyncSession

from ....models.data import GetAwardInfo

from ....models.crud import getAwardByName, getStorage, getUsed, getUser

from ....events.context import OnebotContext
from ....events import root
from ....events.decorator import listenOnebot, matchAlconna, withSessionLock


@listenOnebot(root)
@matchAlconna(Alconna("re:(展示|zhanshi|zs)", Arg("name", str)))
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, result: Arparma):
    name = result.query[str]("name")
    user = await getUser(session, ctx.getSenderId())

    if name is None:
        return

    award = await getAwardByName(session, name)

    if award is None:
        await ctx.reply(UniMessage(f"没有叫 {name} 的小哥"))
        return

    ac = await getStorage(session, user, award)
    au = await getUsed(session, user, award)

    if ac.count + au.count <= 0:
        await ctx.reply(UniMessage(f"你还没有遇到过叫做 {name} 的小哥"))
        return
    
    info = await GetAwardInfo(session, user, award)

    nameDisplay = info.awardName

    if info.skinName is not None:
        nameDisplay += f"[{info.skinName}]"

    await ctx.reply(UniMessage().text(
        nameDisplay + f"【{info.levelName}】"
    ).image(
        path=pathlib.Path(info.awardImg)
    ).text(
        f"\n\n{info.awardDescription}"
    ))
