"""
显示更新信息
"""

import math
from re import Match
from sysconfig import get_platform, get_python_version

import nonebot
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import MessageContext
from src.common.command_deco import limited, listen_message, match_regex
from src.ui.base.browser import get_browser_pool
from src.ui.types.zhuagx import (
    UpdateData,
    get_latest_version,
    get_latest_versions,
    updates,
)


@listen_message()
@limited
@match_regex(r"^(抓小哥|zhua) ?(更新|gx|upd|update)( \d+)?$")
async def _(ctx: MessageContext, res: Match[str]):
    count = 3  # 每页展示的数量
    page = int(res.group(3) or 1)
    short = get_latest_versions(count, page * count - count)
    data = UpdateData(
        current_page=page,
        max_page=math.ceil(len(updates) / count),
        show_pager=True,
        versions=short,
    )
    await ctx.send(
        UniMessage().image(raw=await get_browser_pool().render("update", data))
    )


@listen_message()
@limited
@match_regex("^(抓小哥|zhua) ?(帮助|help)$")
async def _(ctx: MessageContext, *_):
    image = await get_browser_pool().render("help")
    await ctx.send(UniMessage().image(raw=image))


# @listen_message()
# @match_regex("^(关于 ?抓小哥|zhua ?about)$")
# async def _(ctx: MessageContext, *_):
#     await ctx.send(UniMessage().text("关于抓小哥：暂时没"))


@listen_message()
@limited
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

    image = await get_browser_pool().render(
        "about",
        {
            "app_name": app_name,
            "app_version": app_version,
            "kagami_version": get_latest_version().version,
            "python_version": get_python_version(),
            "platform": get_platform(),
        },
    )
    await ctx.send(UniMessage().image(raw=image))
