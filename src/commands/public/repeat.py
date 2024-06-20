from src.common.fast_import import *
from nonebot_plugin_alconna import Image, Text, At, Emoji
import re




@listenPublic()
@matchRegex("^(复读镜)+ ?(.+|\\s+)+")


async def repeat(ctx: PublicContext, match: Match[str]):
    message = await ctx.getMessage()
    msg0 : Text
    msg0 = message[0]
    n = match_list[0]
    msg0o : str = msg0.text
    logger.info(msg0o)
    if len(message) == 1:
        while msg0o.startswith(n) or msg0o.startswith(" "):
            if msg0o.startswith(n) and len(msg0o) > len(n):
                msg0o = msg0o[len(n) :]
            if msg0o.startswith(" ") and len(msg0o) > 1:
                msg0o = msg0o[len(" ") :]
            else:
                break
    else:
        while msg0o.startswith(n) or msg0o.startswith(" "):
            if msg0o.startswith(n) and len(msg0o) > len(n):
                msg0o = msg0o[len(n) :]
            if msg0o.startswith(" ") and len(msg0o) > 1:
                msg0o = msg0o[len(" ") :]
            if msg0o.startswith(n) and len(msg0o) == len(n):
                msg0o = ""
            if msg0o.startswith(" ") and len(msg0o) == 1:
                msg0o = ""
            else:
                break
    logger.info(msg0o)
    _output = UniMessage.text(msg0o)

    for msg in message[1:]:
        if isinstance(msg, Text):
            _output += msg.text
            logger.info(_output)
        elif isinstance(msg,Emoji):
            _output += msg
            logger.info(_output)
        elif isinstance(msg,At):
            _output += msg
            logger.info(_output)
        else:
            break
    if "回收大于0" or "回收小于" in _output:
        await ctx.reply(UniMessage("这样做小镜会伤心的！"))
        return
    
    await ctx.send(_output)

match_list = ["复读镜"]