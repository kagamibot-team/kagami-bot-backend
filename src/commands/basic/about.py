"""
显示更新信息
"""

import PIL
import PIL.Image
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import MessageContext
from src.common.command_decorators import listen_message, match_regex
from src.common.lang.zh import get_latest_versions, la
from src.ui.base.basics import Fonts, render_text, vertical_pile
from src.ui.base.browser import get_browser_pool
from src.ui.base.tools import image_to_bytes

updateHistory: dict[str, list[str]] = la.about.update


@listen_message()
@match_regex("^(抓小哥|zhua) ?(更新|gx|upd|update)$")
async def _(ctx: MessageContext, *_):
    count = 3
    shortHistory = get_latest_versions(count)
    sections: list[PIL.Image.Image] = []

    title = render_text(
        text="更新历史（近三次）",
        color="#63605C",
        font=Fonts.JINGNAN_BOBO_HEI,
        font_size=80,
    )

    for subtitle in shortHistory:
        subtitles: list[PIL.Image.Image] = []
        subtitles.append(
            render_text(
                text=subtitle,
                color="#63605C",
                font=Fonts.JINGNAN_JUNJUN,
                font_size=48,
                margin_bottom=6,
            )
        )
        for commmand in updateHistory[subtitle]:
            subtitles.append(
                render_text(
                    text=commmand,
                    color="#9B9690",
                    font=Fonts.ALIMAMA_SHU_HEI,
                    font_size=24,
                )
            )
        sections.append(vertical_pile(subtitles, 6, "left", "#EEEBE3", 0, 0, 0, 0))

    area_section = vertical_pile(sections, 20, "left", "#EEEBE3", 0, 0, 0, 0)
    img = vertical_pile([title, area_section], 30, "left", "#EEEBE3", 50, 60, 60, 60)
    await ctx.send(UniMessage().image(raw=image_to_bytes(img)))


@listen_message()
@match_regex("^(抓小哥|zhua) ?(帮助|help)$")
async def _(ctx: MessageContext, *_):
    image = await get_browser_pool().render("help")
    await ctx.send(UniMessage().image(raw=image))


@listen_message()
@match_regex("^(关于 ?抓小哥|zhua ?about)$")
async def _(ctx: MessageContext, *_):
    await ctx.send(UniMessage().text(la.about.about))
