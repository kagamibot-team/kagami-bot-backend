from src.imports import *
from src.logic.catch_time import getInterval


@listenPublic()
@requireAdmin()
@matchAlconna(Alconna(["::"], "re:(更改|改变|设置)周期", Arg("interval", int)))
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    interval = res.query[int]("interval")
    assert interval is not None

    if interval < 0:
        await ctx.reply("不要设小于 0 的数谢谢")
        return

    # 调用一下这个接口，保证 Global 对象存在
    await getInterval(session)
    await session.execute(update(Global).values(catch_interval=interval))
    await session.commit()

    await ctx.reply("ok")
