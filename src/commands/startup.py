from src.common.lang.zh import get_latest_version
from src.imports import *


@root.listen(OnebotStartedContext)
async def _(ctx: OnebotStartedContext):
    try:
        await set_qq_status(ctx.bot, QQStatus.在线)
    except ActionFailed as e:
        logger.info(f"在设置在线状态时发生了问题，可能是现在正在使用 LLOnebot 环境而不支持此 API：{e}")
    
    session = get_session()

    async with session.begin():
        try:
            glob = (await session.execute(select(Global.last_reported_version))).scalar_one()
        except Exception as e:
            logger.warning(e)
            await session.execute(delete(Global))
            await session.execute(insert(Global))
            await session.flush()

            glob = (await session.execute(select(Global.last_reported_version))).scalar_one()
        
        if glob != (lv := get_latest_version()):
            await session.execute(update(Global).values(last_reported_version=lv))
            await session.commit()

            msg = f"刚刚推送了版本 {lv} 的更新，内容如下：\n"

            for upd_msg in la.about.update[lv]:
                msg += "\n -" + upd_msg

            await broadcast(ctx.bot, msg)
