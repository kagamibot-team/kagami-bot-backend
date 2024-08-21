from nonebot_plugin_alconna import At, Emoji, Image, Text

from src.base.command_events import GroupContext
from src.base.onebot.onebot_tools import broadcast
from src.common.command_deco import listen_message, require_admin
from src.common.localize_image import localize_image


@listen_message()
@require_admin()
async def _(ctx: GroupContext):
    if len(ctx.message) == 0:
        return

    msg0 = ctx.message[0]
    if not isinstance(msg0, Text):
        return
    if not msg0.text.startswith("::广播"):
        return

    msg = msg0.text[4:]
    if len(msg) > 0 and msg[0] in " \n":
        msg = msg[1:]

    for seg in ctx.message[1:]:
        if isinstance(seg, (Emoji, Text, At)):
            msg += seg
        elif isinstance(seg, Image):
            msg += await localize_image(seg)
        else:
            return

    await broadcast(ctx.bot, msg)
