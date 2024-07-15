import re

from nonebot_plugin_alconna import At, Emoji, Text, UniMessage

from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import listenOnebot


@listenOnebot()
async def repeat(ctx: OnebotContext):
    message = ctx.message
    msg0 = message[0]
    if not isinstance(msg0, Text):
        return
    n = match_list[0]
    msg0o: str = msg0.text
    if not msg0o.startswith(n):
        return
    msg0o_ = msg0o.replace("复读镜 ", "")
    while "复读镜 " in msg0o_:
        msg0o_ = msg0o_.replace("复读镜 ", "")
    while msg0o_.startswith(" "):
        msg0o_ = msg0o_.replace(" ", "")
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
    if re.match("^回收大于0(.)*", _output.extract_plain_text()) or re.match(
        "^回收小于(.)*", _output.extract_plain_text()
    ):
        await ctx.reply(UniMessage("这样做小镜会伤心的..."))
        return

    await ctx.send(_output)


match_list = ["复读镜 "]
