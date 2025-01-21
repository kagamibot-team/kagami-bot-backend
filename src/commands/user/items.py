from re import Match

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_alconna import At, Reply, Text

from src.base.command_events import GroupContext, MessageContext
from src.base.event.event_dispatcher import EventDispatcher
from src.base.event.event_root import root
from src.base.exceptions import KagamiArgumentException
from src.common.command_deco import (
    kagami_exception_handler,
    limit_no_spam,
    match_regex,
    require_admin,
)
from src.core.unit_of_work import get_unit_of_work
from src.logic.admin import is_admin
from src.services.items.base import UseItemArgs, get_item_service

dispatcher = EventDispatcher()


@dispatcher.listen(MessageContext)
@kagami_exception_handler()
@limit_no_spam
@match_regex(r"^(::)?背包 ?(\d+)?$")
async def _(ctx: MessageContext, res: Match[str]):
    # _admin_key = res.group(1) is not None
    _target: str | None = res.group(2)
    if _target is None:
        target = ctx.sender_id
    elif not is_admin(ctx):
        raise KagamiArgumentException("你没有权限查看他人的背包")
    else:
        target = int(_target)

    async with get_unit_of_work(target) as uow:
        isv = get_item_service()
        uid = await uow.users.get_uid(target)
        displays = await isv.get_inventory_displays(uow, uid)

    await ctx.reply(str(displays))


@dispatcher.listen(MessageContext)
@kagami_exception_handler()
@limit_no_spam
async def _(ctx: MessageContext):
    msg = ctx.message
    use_target: int | None = None
    use_keyword: bool = False
    use_name: str | None = None
    for part in msg:
        # print(use_target, use_keyword, use_name, part)
        if isinstance(part, At):
            if use_target is None:
                use_target = int(part.target)
            else:
                return
        elif isinstance(part, Reply):
            if use_target is not None:
                return
            if (
                part.origin is not None
                and isinstance((origin := part.origin), MessageSegment)
                and isinstance(ctx, GroupContext)
            ):
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
            content = part.text
            content = content.replace("\n", " ").replace("\t", " ")
            for word in content.split(" "):
                if word.startswith("使用"):
                    word = word[2:]
                    use_keyword = True
                    word = word.strip()
                if len(word) > 0 and use_name is not None:
                    return
                elif len(word) > 0:
                    use_name = word

    if not use_keyword or use_name is None:
        return

    async with get_unit_of_work() as uow:
        isv = get_item_service()
        item = isv.get_item_strong(use_name)
        arg = UseItemArgs(count=1, target_uid=use_target)
        uid = await uow.users.get_uid(ctx.sender_id)
        data = await item.use(uow, uid, arg)
        await item.send_use_message(ctx, data)


root.link(dispatcher)
