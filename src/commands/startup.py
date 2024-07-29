from loguru import logger
from nonebot import get_driver
from nonebot.exception import ActionFailed
from sqlalchemy import delete, insert, select, update

from src.base.event.event_root import root
from src.base.onebot.onebot_api import send_group_msg, set_qq_status
from src.base.onebot.onebot_enum import QQStatus
from src.base.onebot.onebot_events import OnebotStartedContext
from src.base.onebot.onebot_tools import broadcast
from src.common.config import config
from src.common.lang.zh import get_latest_version, la
from src.core.unit_of_work import get_unit_of_work
from src.models.models import Global


@root.listen(OnebotStartedContext)
async def _(ctx: OnebotStartedContext):
    try:
        await set_qq_status(ctx.bot, QQStatus.在线)
    except ActionFailed as e:
        logger.info(
            f"在设置在线状态时发生了问题，可能是现在正在使用 LLOnebot 环境而不支持此 API：{e}"
        )

    async with get_unit_of_work() as uow:
        session = uow.session
        try:
            glob = (
                await session.execute(select(Global.last_reported_version))
            ).scalar_one()
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(e)
            await session.execute(delete(Global))
            await session.execute(insert(Global))
            await session.flush()

            glob = (
                await session.execute(select(Global.last_reported_version))
            ).scalar_one()

        if glob != (lv := get_latest_version()):
            await session.execute(
                update(Global).values({Global.last_reported_version: lv})
            )
            msg = f"刚刚推送了版本 {lv} 的更新，内容如下：\n"

            for upd_msg in la.about.update[lv]:
                msg += "\n -" + upd_msg

            await broadcast(ctx.bot, msg)
        elif get_driver().env != "dev":
            for group in config.admin_groups:
                await send_group_msg(ctx.bot, group, "服务器重启好了")
