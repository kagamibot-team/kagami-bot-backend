import re

from nonebot_plugin_alconna import At, Emoji, Text, UniMessage

from src.base.command_events import MessageContext
from src.common.command_deco import debug_only, listen_message


@listen_message()
@debug_only()
async def repeat(ctx: MessageContext):
    message = ctx.message
    if len(message) == 0:
        return
    msg0 = message[0]
    if not isinstance(msg0, Text):
        return
    msg0o: str = msg0.text
    if not msg0o.startswith("复读镜 "):
        return

    msg0o_ = msg0o.replace("复读镜 ", "").lstrip()
    if len(msg0o_) == 0 and len(message) == 1:
        return

    if len(msg0o_) == 0:
        msg0o_ = ""

    _output = UniMessage.text(msg0o_)
    for msg in message[1:]:
        if isinstance(msg, Text):
            _output += msg.text
        elif isinstance(msg, Emoji):
            _output += msg
        elif isinstance(msg, At):
            _output += msg
        else:
            break

    if re.match("^回收(大于0|小于)(.)*", _output.extract_plain_text()):
        await ctx.reply(UniMessage("这样做小镜会伤心的..."))
    else:
        await ctx.send(_output)
