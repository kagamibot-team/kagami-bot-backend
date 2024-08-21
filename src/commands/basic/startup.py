from loguru import logger
from nonebot import get_driver
from nonebot.exception import ActionFailed

from src.base.event.event_root import root
from src.base.onebot.onebot_api import get_group_list, send_group_msg, set_qq_status
from src.base.onebot.onebot_enum import QQStatus
from src.base.onebot.onebot_events import OnebotStartedContext
from src.base.onebot.onebot_tools import broadcast, update_cached_name
from src.common.command_deco import interval_at_start
from src.common.config import config
from src.common.lang.zh import get_latest_version, la
from src.core.unit_of_work import get_unit_of_work


@root.listen(OnebotStartedContext)
async def _(ctx: OnebotStartedContext):
    try:
        await set_qq_status(ctx.bot, QQStatus.在线)
    except ActionFailed as e:
        logger.info(f"没有更改在线状态，正在使用的框架很有可能是 LLOnebot。{e}")

    async with get_unit_of_work() as uow:
        version = await uow.settings.get_last_version()
        lv = get_latest_version()

        if version != lv:
            await uow.settings.set_last_version(lv)

            msg = f"刚刚推送了版本 {lv} 的更新，内容如下：\n"
            for upd_msg in la.about.update[lv]:
                msg += "\n -" + upd_msg
            await broadcast(ctx.bot, msg)
        elif get_driver().env != "dev":
            for group in config.admin_groups:
                await send_group_msg(ctx.bot, group, "服务器重启好了")


@interval_at_start(60, False)
async def _(ctx: OnebotStartedContext):
    ls = await get_group_list(ctx.bot)
    for info in ls:
        await update_cached_name(ctx.bot, info.group_id)
