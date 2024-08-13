from nonebot_plugin_alconna import At, Emoji, Reply, Text, UniMessage
from src.base.command_events import OnebotContext
from src.common.command_decorators import listen_message
from src.common.data.awards import use_award
from src.common.rd import get_random
from nonebot.adapters.onebot.v11 import MessageSegment

from src.core.unit_of_work import get_unit_of_work


@listen_message()
async def _(ctx: OnebotContext):
    is_throw = False
    is_poop = False
    target: set[int] = set()

    for segment in ctx.message:
        if isinstance(segment, Text):
            text = segment.text
            for i in ("史", "石", "屎", "粑粑", "💩", "大便", "便便", "大变", "大便"):
                if i in text:
                    is_poop = True
            for i in ("丢", "扔", "抛", "吃", "赤"):
                if i in text:
                    is_throw = True
            for i in ("不", "别", "莫", "讨厌"):
                if i in text:
                    return
        elif isinstance(segment, At):
            target.add(int(segment.target))
        elif isinstance(segment, Reply):
            if segment.origin is not None and isinstance(
                (msg := segment.origin), MessageSegment
            ):
                msgid: str | None = msg.data.get("id", None)
                if msgid is None:
                    continue
                res = await ctx.bot.call_api("get_msg", message_id=msgid)
                sender_obj = res.get("sender", None)
                if sender_obj is None:
                    return
                uid = sender_obj.get("user_id", None)
                if uid is None:
                    return
                target.add(int(uid))
        elif isinstance(segment, Emoji):
            if segment.id == "59":
                is_poop = True
        else:
            return

    if not is_throw or not is_poop or len(target) != 1:
        return

    p = target.pop()
    if str(p) == ctx.bot.self_id:
        return

    # 扔粑粑
    successed = get_random().random() < 0.5

    async with get_unit_of_work(ctx.sender_id) as uow:
        fuid = await uow.users.get_uid(ctx.sender_id)
        tuid = await uow.users.get_uid(p)

        poop = await uow.awards.get_aid("粑粑小哥")
        if poop is None:
            return
        await use_award(uow, fuid, poop, 1)
        if successed:
            await uow.inventories.give(tuid, poop, 1)

    msg = UniMessage.text("你向 ").at(user_id=str(p)).text(" 扔出去了一个粑粑小哥")
    if successed:
        msg.text("，扔中了，粑粑小哥爬到了他的库存里面")
    else:
        msg.text("，没扔中，粑粑小哥在地里烂掉了")

    await ctx.reply(msg)
