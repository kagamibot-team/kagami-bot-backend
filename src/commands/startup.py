from src.imports import *


@root.listen(OnebotStartedContext)
async def _(ctx: OnebotStartedContext):
    try:
        await set_qq_status(ctx.bot, QQStatus.在线)
    except ActionFailed as e:
        logger.info(f"在设置在线状态时发生了问题，可能是现在正在使用 LLOnebot 环境而不支持此 API：{e}")
