from nonebot import on_type
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

    if set(text[2:]) <= set("!！?？。., 1"):
        return text[2:]


@eventMatcher.handle()
async def ping(bot: Bot, event: GroupMessageEvent):
    message = event.get_plaintext()

    match = matchKagami(message)

    if match != None:
        if event.sender.user_id == 3485988098:
            await eventMatcher.finish("此方" + match)
        if event.sender.user_id == 1728332155:
            await eventMatcher.finish("小司" + match)
        if event.sender.user_id == 514827965:
            await eventMatcher.finish("PT" + match)
        if event.sender.user_id == 943551369:
            await eventMatcher.finish("给" + match)
        if event.sender.user_id == 1738376213:
            await eventMatcher.finish("Kecay" + match)
        if event.sender.user_id == 2873881986:
            await eventMatcher.finish("赤蛮奇" + match)
        if event.sender.user_id == 1467858478:
            await eventMatcher.finish("贪吃小哥" + match)
        if event.sender.user_id == 602528231:
            await eventMatcher.finish("小槽" + match)
        if event.sender.user_id == 3043069014:
            await eventMatcher.finish("小阿" + match)

        await eventMatcher.finish("在" + match)


tellMeIp = on_type(types=PrivateMessageEvent)


@tellMeIp.handle()
async def ping2(event: PrivateMessageEvent):
    if event.get_plaintext() == "::getip":
        if event.sender.user_id != 514827965:
            return

        localhost_name = socket.gethostname()
        ips = socket.gethostbyname_ex(localhost_name)[2]

        await tellMeIp.finish(Message(MessageSegment.text("\n".join(ips))))
