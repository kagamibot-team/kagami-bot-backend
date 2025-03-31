"""
显示更新信息
"""

import math
from re import Match
from sysconfig import get_platform, get_python_version

import nonebot

from src.base.command_events import MessageContext
from src.base.exceptions import ObjectNotFoundException
from src.common.command_deco import listen_message, match_regex
from src.ui.base.render import get_render_pool
from src.ui.types.zhuagx import (UpdateData, get_latest_version,
                                 get_latest_versions, updates)
from src.ui.types.zhuahelp import HelpData, command_content, command_dict


@listen_message()
@match_regex(r"^(抓小哥|zhua) ?(更新|gx|upd|update)( \d*)?$")
async def _(ctx: MessageContext, res: Match[str]):
    count = 3  # 每页展示的数量
    page = (res.group(3) or "").strip()
    if page == "":
        page = 1
    else:
        page = int(page)
    short = get_latest_versions(count, page * count - count)
    data = UpdateData(
        current_page=page,
        max_page=math.ceil(len(updates) / count),
        show_pager=True,
        versions=short,
    )
    image = await get_render_pool().render("update", data)
    await ctx.send_image(image)


@listen_message()
@match_regex(r"^(抓小哥|zhua) ?(帮助|help)( .+)?$")
async def _(ctx: MessageContext, res: Match[str]):
    command = (res.group(3) or "").strip()
    if command == "":
        image = await get_render_pool().render("help")
    else:
        if command not in command_dict:
            raise ObjectNotFoundException("指令")
        data: HelpData = command_content[command_dict[command]]
        image = await get_render_pool().render("help/detail", data)
    await ctx.send_image(image)


@listen_message()
@match_regex("^(关于 ?小?镜 ?([bB]ot)?|kagami ?about)$")
async def _(ctx: MessageContext, *_):
    try:
        bot = nonebot.get_bot()
        onebot_meta = await bot.call_api("get_version_info")

        app_name: str = onebot_meta["app_name"]
        app_version: str = onebot_meta["app_version"]
    except:
        app_name: str = "未识别"
        app_version: str = "未识别"

    image = await get_render_pool().render(
        "about",
        {
            "app_name": app_name,
            "app_version": app_version,
            "kagami_version": get_latest_version().version,
            "python_version": get_python_version(),
            "platform": get_platform(),
        },
    )
    await ctx.send_image(image)
