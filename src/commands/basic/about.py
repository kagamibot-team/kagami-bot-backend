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
from src.ui.types.zhuahelp import HelpData, command_dict, command_content
from src.base.exceptions import ObjectNotFoundException


@listen_message()
@limited
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
    image = await get_browser_pool().render("update", data)
    await ctx.send(UniMessage().image(raw=image))


@listen_message()
@limited
@match_regex(r"^(抓小哥|zhua) ?(帮助|help)( .+)?$")
async def _(ctx: MessageContext, res: Match[str]):
    command = (res.group(3) or "").strip()
    if command == "":
        image = await get_browser_pool().render("help")
    else:
        if command not in command_dict:
            raise ObjectNotFoundException("指令")
        data: HelpData = command_content[command_dict[command]]
        image = await get_browser_pool().render("help/detail", data)
    await ctx.send(UniMessage().image(raw=image))


@listen_message()
@limited
@match_regex("^(关于 ?小?镜 ?([bB]ot)?|kagami ?about)$")
async def _(ctx: MessageContext, *_):
    image = await get_browser_pool().render("about")
    await ctx.send(UniMessage().image(raw=image))
