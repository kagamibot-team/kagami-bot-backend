"""
小镜！！！
"""


import asyncio
import re
from nonebot_plugin_alconna import UniMessage

from ...commands.basics.loading import withLoading

from ...config import config
from ...events import PublicContext, root

from ...events.decorator import listenPublic, matchRegex


@listenPublic()
@matchRegex("^[小|柊]镜([!！?？。.,， 1;；：:'‘’\"“”]*)$")
async def ping(ctx: PublicContext, res: re.Match[str]):
    sgns = res.group(1)
    sender = ctx.getSenderId()
    custom_replies = config.custom_replies

    if sender is None:
        await ctx.send(UniMessage("在" + sgns))
        return
    
    if (k := str(sender)) in custom_replies.keys():
        await ctx.send(UniMessage(custom_replies[k] + sgns))
        return
    
    await ctx.send(UniMessage("在" + sgns))


@listenPublic()
@matchRegex("^[小|柊]镜[， ,]?跳?科目三$")
@withLoading("")
async def _(ctx: PublicContext, _: re.Match[str]):
    await asyncio.sleep(5)
