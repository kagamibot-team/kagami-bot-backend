"""
小镜！！！
"""


import asyncio
from src.common.fast_import import *


def __match_char(c: str):
    o = ord(c)

    if 0x20 <= o <= 0x2f:
        return True
    if 0x3A <= o <= 0x40:
        return True
    if 0x5B <= o <= 0x60:
        return True
    if 0x7B <= o <= 0x7E:
        return True
    if 0xA0 <= o <= 0xBF or o == 0xD7 or o == 0xF7:
        return True
    
    # https://en.wikipedia.org/wiki/Unicode_symbol
    # 字母数字变体
    if 0x20A0 <= o <= 0x20CF:
        return True
    if 0x2000 <= o <= 0x206F:
        return True
    if 0x2100 <= o <= 0x214F:
        return True
    
    # 箭头
    if 0x2190 <= o <= 0x21FF:
        return True
    if 0x2794 <= o <= 0x27BF:
        return True
    if 0x2B00 <= o <= 0x2BFF:
        return True
    if 0x27F0 <= o <= 0x27FF:
        return True
    if 0x2900 <= o <= 0x297F:
        return True
    if 0x1F800 <= o <= 0x1F8FF:
        return True
    
    # Emoji 符号
    if 0x2700 <= o <= 0x27BF:
        return True
    if 0x1F600 <= o <= 0x1F64F:
        return True
    if 0x2600 <= o <= 0x26FF:
        return True
    if 0x1F300 <= o <= 0x1F5FF:
        return True
    if 0x1F900 <= o <= 0x1F9FF:
        return True
    if 0x1FA70 <= o <= 0x1FAF8:
        return True
    if 0x1F680 <= o <= 0x1F9FF:
        return True
    
    return False


def __match_str(s: str):
    for c in s:
        if not __match_char(c):
            return False
    
    return True


# @listenPublic()
@listenConsole()
@matchRegex("^[小|柊]镜([!！?？。.,， 1;；：:'‘’\"“”]*)$")
async def _(ctx: ConsoleContext, res: Match[str]):
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


@listenOnebot()
async def _(ctx: OnebotContext):
    message = await ctx.getMessage()
    if len(message) == 0:
        return
    if not isinstance((msg0 := message[0]), Text):
        return
    if not msg0.text.startswith(("小镜", "柊镜")):
        return
    if not __match_str(msg0.text[2:]):
        return
    
    rep_name = la.msg.default_reply
    sender = ctx.getSenderId()
    custom_replies = config.custom_replies
    if (k := str(sender)) in custom_replies.keys():
        rep_name = custom_replies[k]

    _output = UniMessage.text(rep_name + msg0.text[2:])

    for msg in message[1:]:
        if isinstance(msg, Text):
            if not __match_str(msg.text):
                return
            _output += UniMessage.text(msg.text)
        if isinstance(msg, Emoji):
            _output += msg
        else:
            return

    await ctx.send(_output)


@listenPublic()
@matchRegex("^[小|柊]镜[， ,]?跳?科目三$")
@withLoading("")
async def _(ctx: PublicContext, _: Match[str]):
    await asyncio.sleep(5)

