"""
在目前的开发阶段，有很多需要用到的功能，例如同步存档之类。
如果有一些需要方便开发的指令，就写到这里吧！
"""

import json
from pathlib import Path
from re import Match

from nonebot_plugin_alconna import UniMessage

from src.base.command_events import GroupContext, MessageContext, OnebotContext
from src.base.db import DatabaseManager
from src.base.onebot.onebot_api import get_group_list
from src.base.onebot.onebot_tools import update_cached_name
from src.common.command_deco import (
    listen_message,
    match_literal,
    match_regex,
    require_admin,
)
from src.common.save_file_handler import pack_save

from src.apis.render_ui import manager as backend_data_manager


@listen_message()
@require_admin()
@match_literal("::manual-save")
async def _(ctx: MessageContext):
    await DatabaseManager.get_single().manual_checkpoint()
    await ctx.reply("ok")


@listen_message()
@require_admin()
@match_regex(
    "^:: ?(导出|输出|保存|发送|生成|构建|建造|吐出|献出) ?(你(自己)?的)? ?(存档|文件|心脏|大脑)$"
)
async def _(ctx: GroupContext, _):
    await DatabaseManager.get_single().manual_checkpoint()
    fp = await pack_save()
    await ctx.bot.call_api(
        "upload_group_file",
        group_id=ctx.event.group_id,
        file=str(fp.absolute()),
        name=fp.name,
    )


@listen_message()
@require_admin()
@match_regex("^::导出日志$")
async def _(ctx: GroupContext, _):
    await DatabaseManager.get_single().manual_checkpoint()
    fp = Path("./data/log.log")
    await ctx.bot.call_api(
        "upload_group_file",
        group_id=ctx.event.group_id,
        file=str(fp.absolute()),
        name=fp.name,
    )


@listen_message()
@require_admin()
@match_regex("^::dump-data ([0-9a-fA-F]+)$")
async def _(ctx: MessageContext, res: Match[str]):
    data = backend_data_manager.get(res.group(1))
    if data is not None:
        if isinstance(data, dict):
            await ctx.reply(UniMessage(json.dumps(data)))
        else:
            await ctx.reply(UniMessage(str(data.model_dump_json(indent=4))))
    else:
        await ctx.reply("None.")


@listen_message()
@require_admin()
@match_literal("::refresh-card")
async def _(ctx: OnebotContext):
    groups = await get_group_list(ctx.bot)
    for info in groups:
        await update_cached_name(ctx.bot, info.group_id)
    await ctx.reply("ok.")
