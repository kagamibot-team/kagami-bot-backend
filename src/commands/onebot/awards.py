import pathlib


from src.common.fast_import import *


@listenOnebot()
@matchAlconna(Alconna("re:(展示|zhanshi|zs)", Arg("name", str)))
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, result: Arparma):
    name = result.query[str]("name")
    user = await qid2did(session, ctx.getSenderId())

    if name is None:
        return

    award = await getAidByName(session, name)

    if award is None:
        await ctx.reply(UniMessage(f"没有叫 {name} 的小哥"))
        return

    if await getStatistics(session, user, award) <= 0:
        await ctx.reply(UniMessage(f"你还没有遇到过叫做 {name} 的小哥"))
        return

    info = await getAwardInfo(session, user, award)
    nameDisplay = info.awardName

    if info.skinName is not None:
        nameDisplay += f"[{info.skinName}]"

    await ctx.reply(
        UniMessage()
        .text(nameDisplay + f"【{info.levelName}】")
        .image(path=pathlib.Path(info.awardImg))
        .text(f"\n{info.awardDescription}")
    )
