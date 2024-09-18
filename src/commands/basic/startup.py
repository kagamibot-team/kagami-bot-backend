from loguru import logger
from nonebot import get_driver
from nonebot.exception import ActionFailed
from nonebot_plugin_alconna import UniMessage

from src.base.event.event_root import root
from src.base.onebot.onebot_api import get_group_list, send_group_msg, set_qq_status
from src.base.onebot.onebot_enum import QQStatus
from src.base.onebot.onebot_events import OnebotStartedContext
from src.base.onebot.onebot_tools import broadcast, update_cached_name
from src.common.command_deco import interval_at_start
from src.common.config import get_config
from src.common.webhook import send_webhook
from src.core.unit_of_work import get_unit_of_work
from src.ui.base.render import get_render_pool
from src.ui.types.zhuagx import UpdateData, get_latest_version


@root.listen(OnebotStartedContext)
async def _(ctx: OnebotStartedContext):
    try:
        await set_qq_status(ctx.bot, QQStatus.在线)
    except ActionFailed as e:
        logger.info(f"没有更改在线状态，正在使用的框架很有可能是 LLOnebot。{e}")

    async with get_unit_of_work() as uow:
        version = await uow.settings.get_last_version()
        lv = get_latest_version()
        await uow.settings.set_last_version(lv.version)

    if version != lv.version:
        data = UpdateData(versions=[lv], show_pager=False)
        msg = UniMessage.image(raw=await get_render_pool().render("update", data))
        await broadcast(ctx.bot, msg)
    elif get_driver().env != "dev":
        for group in get_config().admin_groups:
            await send_group_msg(ctx.bot, group, "服务器重启好了")

    if get_config().enable_web_hook:
        if get_config().bot_start_webhook:
            await send_webhook(
                get_config().bot_start_webhook, {"message": "bot_started"}
            )


if (itv := get_config().reload_info_interval) > 0:

    @interval_at_start(itv, False)
    async def _(ctx: OnebotStartedContext):
        ls = await get_group_list(ctx.bot)
        for info in ls:
            await update_cached_name(ctx.bot, info.group_id)


if (itv := get_config().clean_browser_interval) > 0:

    @interval_at_start(itv, True)
    async def _(ctx: OnebotStartedContext):
        pool = get_render_pool()
        await pool.clean()
