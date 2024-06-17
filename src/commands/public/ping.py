"""
小镜！！！
"""


import asyncio
from src.common.fast_import import *


@listenPublic()
@matchRegex("^[小|柊]镜([!！?？。.,， 1;；：:'‘’\"“”]*)$")
async def ping(ctx: PublicContext, res: Match[str]):
    sgns = res.group(1)
    sender = ctx.getSenderId()
    custom_replies = config.custom_replies

    if sender is None:
        await ctx.send(UniMessage(la.msg.default_reply + sgns))
        return
    
    if (k := str(sender)) in custom_replies.keys():
        await ctx.send(UniMessage(custom_replies[k] + sgns))
        return
    
    await ctx.send(UniMessage(la.msg.default_reply + sgns))


@listenPublic()
@matchRegex("^[小|柊]镜[， ,]?跳?科目三$")
@withLoading("")
async def _(ctx: PublicContext, _: Match[str]):
    await asyncio.sleep(5)
