from src.imports import *


@root.listen(OnebotStartedContext)
async def _(ctx: OnebotStartedContext):
    await set_qq_status(ctx.bot, QQStatus.在线)
