"""
显示更新信息
"""

import math
from re import Match
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import MessageContext
from src.common.command_deco import limited, listen_message, match_regex
from src.ui.base.browser import get_browser_pool
from src.ui.types.zhuagx import UpdateData, get_latest_versions, updates


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
    image = await get_browser_pool().render("about")
    await ctx.send(UniMessage().image(raw=image))
