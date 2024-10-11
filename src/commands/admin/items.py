from re import Match

from nonebot_plugin_alconna import At, Reply, Text
from src.base.command_events import GroupContext, MessageContext
from src.base.event.event_dispatcher import EventDispatcher
from src.common.command_deco import match_regex, require_admin
from src.core.unit_of_work import get_unit_of_work
from src.services.items.base import get_item_service
from nonebot.adapters.onebot.v11 import MessageSegment


dispatcher = EventDispatcher()


@dispatcher.listen(MessageContext)
@require_admin()
@match_regex(r"^::背包 ?(\d+)?$")
async def _(ctx: MessageContext, res: Match[str]):
    _target: str | None = res.group(1)
    if _target is None:
        target = ctx.sender_id
    else:
        target = int(_target)

    async with get_unit_of_work(target) as uow:
        isv = get_item_service()
        uid = await uow.users.get_uid(target)
        displays = await isv.get_inventory_displays(uow, uid)

    await ctx.reply(str(displays))


@dispatcher.listen(MessageContext)
@require_admin()
async def _(ctx: MessageContext):
    msg = ctx.message
    use_target: int | None = None
    use_keyword: bool = False
    use_name: str | None = None
    for part in msg:
        if isinstance(part, At):
            if use_target is None:
                use_target = int(part.target)
            else:
                return
        elif isinstance(part, Reply):
            if use_target is not None:
                return
            if part.origin is not None and isinstance((origin:=part.origin), MessageSegment) and isinstance(ctx, GroupContext):
                msgid: str | None = origin.data.get("id", None)
                if msgid is None:
                    continue
                res = await ctx.bot.call_api("get_msg", message_id=msgid)
                sender_obj = res.get("sender", None)
                if sender_obj is None:
                    return
                uid = sender_obj.get("user_id", None)
                if uid is None:
                    return
                use_target = int(uid)
        elif isinstance(part, Text):
            ...
