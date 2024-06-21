"""
显示更新信息
"""

from src.imports import *


updateHistory: dict[str, list[str]] = la.about.update
updateHistoryDev: dict[str, list[str]] = la.about.update_dev
help: list[str] = la.about.help
helpAdmin: list[str] = la.about.help_admin


def constructUpdateMessage(updates: dict[str, list[str]], count: int = 5) -> UniMessage:
    """
    构造更新信息
    """

    text = f"{la.about.update_header}\n"

    for key in sorted(updates.keys(), reverse=True):
        if count == 0:
            break

        count -= 1
        text += f"{key}:\n"
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
    await ctx.send(constructUpdateMessage(updateHistory))


@listenPublic()
@matchRegex("^:: ?(抓小哥|zhua) ?(更新|gx|upd|update)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructUpdateMessage(updateHistoryDev))


@listenPublic()
@matchRegex("^(抓小哥|zhua) ?(帮助|help)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructHelpMessage(help))


@listenPublic()
@matchRegex("^:: ?(抓小哥|zhua) ?(帮助|help)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructHelpMessage(helpAdmin))


@listenPublic()
@matchRegex("^(关于 ?抓小哥|zhua ?about)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(UniMessage().text(la.about.about))
