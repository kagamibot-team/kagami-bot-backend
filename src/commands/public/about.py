"""
显示更新信息
"""

from src.common.lang.zh import get_latest_versions
from src.imports import *
from packaging.version import Version


updateHistory: dict[str, list[str]] = la.about.update
updateHistoryDev: dict[str, list[str]] = la.about.update_dev
help: dict[str, list[str]] = la.about.help
helpAdmin: list[str] = la.about.help_admin


def constructUpdateMessage(updates: dict[str, list[str]], count: int = 3) -> UniMessage:
    """
    构造更新信息
    """

    text = f"{la.about.update_header}\n"

    for key in get_latest_versions(count):
        text += f"版本 {key} 更新推送:\n"
        for item in updates[key]:
            text += f"- {item}\n"

    return UniMessage().text(text)


def constructHelpMessage(helps: list[str]) -> UniMessage:
    """
    构造帮助信息
    """

    text = f"{la.about.help_header}\n"

    for item in helps:
        text += f"- {item}\n"

    return UniMessage().text(text)


@listenPublic()
@matchRegex("^(抓小哥|zhua) ?(更新|gx|upd|update)$")
async def _(ctx: PublicContext, *_):
    count = 3
    shortHistory = get_latest_versions(count)
    sections: list[PIL.Image.Image] = []

    title = await getTextImage(
        text="更新历史（近三次）",
        color="#63605C",
        font=Fonts.JINGNAN_BOBO_HEI,
        font_size=80,
    )

    for subtitle in shortHistory:
        subtitles: list[PIL.Image.Image] = []
        subtitles.append(
            await getTextImage(
                text=subtitle,
                color="#63605C",
                font=Fonts.JINGNAN_JUNJUN,
                font_size=48,
                margin_bottom=6,
            )
        )
        for commmand in updateHistory[subtitle]:
            subtitles.append(
                await getTextImage(
                    text=commmand,
                    color="#9B9690",
                    font=Fonts.ALIMAMA_SHU_HEI,
                    font_size=24,
                )
            )
        sections.append(await verticalPile(subtitles, 6, "left", "#EEEBE3", 0, 0, 0, 0))

    area_section = await verticalPile(sections, 20, "left", "#EEEBE3", 0, 0, 0, 0)
    img = await verticalPile(
        [title, area_section], 30, "left", "#EEEBE3", 50, 60, 60, 60
    )
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))


@listenPublic()
@matchRegex("^:: ?(抓小哥|zhua) ?(更新|gx|upd|update)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructUpdateMessage(updateHistoryDev))


@listenPublic()
@matchRegex("^(抓小哥|zhua) ?(帮助|help)$")
async def _(ctx: PublicContext, *_):
    sections: list[PIL.Image.Image] = []

    title = await getTextImage(
        text="指令列表",
        color="#63605C",
        font=Fonts.JINGNAN_BOBO_HEI,
        font_size=80,
    )

    for subtitle, commands in help.items():
        subtitles: list[PIL.Image.Image] = []
        subtitles.append(
            await getTextImage(
                text=subtitle,
                color="#63605C",
                font=Fonts.JINGNAN_JUNJUN,
                font_size=48,
                margin_bottom=6,
            )
        )
        for commmand in commands:
            subtitles.append(
                await getTextImage(
                    text=commmand,
                    color="#9B9690",
                    font=Fonts.ALIMAMA_SHU_HEI,
                    font_size=24,
                )
            )
        sections.append(await verticalPile(subtitles, 6, "left", "#EEEBE3", 0, 0, 0, 0))

    area_section = await verticalPile(sections, 20, "left", "#EEEBE3", 0, 0, 0, 0)
    img = await verticalPile(
        [title, area_section], 30, "left", "#EEEBE3", 50, 60, 60, 60
    )
    await ctx.send(UniMessage().image(raw=imageToBytes(img)))


@listenPublic()
@matchRegex("^:: ?(抓小哥|zhua) ?(帮助|help)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructHelpMessage(helpAdmin))


@listenPublic()
@matchRegex("^(关于 ?抓小哥|zhua ?about)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(UniMessage().text(la.about.about))
