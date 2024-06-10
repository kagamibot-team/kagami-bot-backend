import re
from nonebot import get_driver, on_type
from nonebot.plugin import on
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    PrivateMessageEvent,
    Message,
    MessageSegment,
)

import socket


eventMatcher = on_type(types=GroupMessageEvent)


def matchKagami(text: str):
    if len(text) < 2 or (text[:2] != "小镜" and text[:2] != "柊镜"):
        return

    # if set(text[2:]) <= set("!！?？。.,， 1;；：:'‘’\"“”"):
    if re.match(get_driver().config.re_match_rule, text[2:]):
        return text[2:]


@eventMatcher.handle()
async def ping(bot: Bot, event: GroupMessageEvent):
    message = event.get_plaintext()

    match = matchKagami(message)

    if match != None:
        cr = get_driver().config.custom_replies
        us = str(event.sender.user_id)

        if us in cr.keys():
            await eventMatcher.finish(cr[us] + match)

        await eventMatcher.finish("在" + match)


tellMeIp = on_type(types=PrivateMessageEvent)


@tellMeIp.handle()
async def ping2(event: PrivateMessageEvent):
    if event.get_plaintext() == "::getip":
        if event.sender.user_id != get_driver().config.admin_id:
            return

        localhost_name = socket.gethostname()
        ips = socket.gethostbyname_ex(localhost_name)[2]

        await tellMeIp.finish(Message(MessageSegment.text("\n".join(ips))))
