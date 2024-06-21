"""
小镜！！！
"""

from src.imports import *


def __match_char(c: str):
    o = ord(c)

    rules = (
        # ASCII 范围内的符号
        0x20 <= o <= 0x2F,
        0x3A <= o <= 0x40,
        0x5B <= o <= 0x60,
        0x7B <= o <= 0x7E,
        0xA0 <= o <= 0xBF,
        o == 0xD7,
        o == 0xF7,
        # ==================
        # https://en.wikibooks.org/wiki/Unicode/Character_reference/F000-FFFF
        # ==================
        # 全宽符号与半宽符号变种
        0xFF01 <= o <= 0xFF20,
        0xFF3B <= o <= 0xFF40,
        0xFF5B <= o <= 0xFF65,
        0xFFE0 <= o <= 0xFFEE,
        # CJK 标点兼容与纵排符号
        0xFE10 <= o <= 0xFE19,
        0xFE30 <= o <= 0xFE4F,
        # Small Form Variants
        0xFE50 <= o <= 0xFE6B,
        # Combining Half Marks
        0xFE20 <= o <= 0xFE2F,
        # 错误符号
        o == 0xFFFD,
        # ==================
        # https://en.wikipedia.org/wiki/Unicode_symbol
        # https://en.wikipedia.org/wiki/Punctuation
        # ==================
        # 字母数字变体
        0x20A0 <= o <= 0x20CF,
        0x2000 <= o <= 0x206F,
        0x2100 <= o <= 0x214F,
        # 箭头
        0x2190 <= o <= 0x21FF,
        0x2794 <= o <= 0x27BF,
        0x2B00 <= o <= 0x2BFF,
        0x27F0 <= o <= 0x27FF,
        0x2900 <= o <= 0x297F,
        0x1F800 <= o <= 0x1F8FF,
        # Emoji 符号
        0x2700 <= o <= 0x27BF,
        0x1F600 <= o <= 0x1F64F,
        0x2600 <= o <= 0x26FF,
        0x1F300 <= o <= 0x1F5FF,
        0x1F900 <= o <= 0x1F9FF,
        0x1FA70 <= o <= 0x1FAF8,
        0x1F680 <= o <= 0x1F9FF,
    )

    for rule in rules:
        if rule:
            return True

    return False


def __match_str(s: str):
    for c in s:
        if not __match_char(c):
            return False

    return True


@listenPublic()
async def _(ctx: UniMessageContext):
    message = await ctx.getMessage()
    if len(message) == 0:
        return
    if not isinstance((msg0 := message[0]), Text):
        return

    msg0o: str | None = None

    for name in config.my_name:
        if msg0.text.startswith(name):
            msg0o = msg0.text[len(name) :]
            break

    if msg0o is None:
        return

    if not __match_str(msg0o):
        return

    rep_name = la.msg.default_reply
    sender = ctx.getSenderId()
    custom_replies = config.custom_replies
    if (k := str(sender)) in custom_replies.keys():
        rep_name = custom_replies[k]

    _output = UniMessage.text(rep_name + msg0o)

    for msg in message[1:]:
        if isinstance(msg, Text):
            if not __match_str(msg.text):
                return
            _output += UniMessage.text(msg.text)
        elif isinstance(msg, Emoji):
            _output += msg
        else:
            return

    await ctx.send(_output)
