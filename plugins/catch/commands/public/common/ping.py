"""
小镜！！！
"""


import re
from nonebot_plugin_alconna import UniMessage

from ....config import config
from ....events import PublicContext, EventManager, OnebotMessageContext, ConsoleMessageContext

from ...classes.decorator import matchRegex


manager = EventManager()


@manager.listens(OnebotMessageContext, ConsoleMessageContext)
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
