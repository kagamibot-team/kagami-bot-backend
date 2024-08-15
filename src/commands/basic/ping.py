from pathlib import Path
import time
from nonebot_plugin_alconna import At, Emoji, Text, UniMessage
from src.base.command_events import GroupContext, MessageContext
from src.base.event.event_root import root
from src.base.onebot.onebot_api import (
    get_name,
    send_group_msg,
    send_private_msg,
)
from src.base.onebot.onebot_basic import OnebotBotProtocol
from src.base.onebot.onebot_enum import QQEmoji
from src.base.onebot.onebot_events import GroupPokeContext
from src.common.command_decorators import listen_message, require_awake
from src.common.config import config
from src.common.rd import get_random
from src.core.unit_of_work import get_unit_of_work


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
        0x3000 <= o <= 0x303F,
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


@listen_message()
@require_awake
async def _(ctx: MessageContext):
    message = ctx.message
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

    rep_name = "在"
    sender = ctx.sender_id
    async with get_unit_of_work(ctx.sender_id) as uow:
        custom_reply = await uow.users.name(qqid=sender)
    if custom_reply is not None:
        rep_name = custom_reply

    _output = UniMessage.text(rep_name + msg0o)

    for msg in message[1:]:
        if isinstance(msg, Text):
            if not __match_str(msg.text):
                return
            _output += UniMessage.text(msg.text)
        elif isinstance(msg, Emoji):
            if msg.id == "415":
                continue
            _output += msg
        else:
            return

    await ctx.send(_output)


async def reply_call(
    bot: OnebotBotProtocol, group: int | None, sender: int, sender_name: str
):
    at_back = UniMessage.at(str(sender))
    async with get_unit_of_work(sender) as uow:
        special_name = await uow.users.name(qqid=sender)

    _special = (
        (
            f"哇！是{special_name}",
            f"呼呼！{special_name}",
            f"{special_name}，我一直都在哟☆",
            f"嗯哼 {special_name}",
            f"爱你！{special_name}！"
            + UniMessage.emoji(id="66").emoji(id="66").emoji(id="66"),
        )
        if special_name
        else ()
    )

    message = get_random().choice(
        (
            "诶嘿！",
            at_back + " 在的哦！",
            "owo",
            "我在。",
            at_back + " 怎么戳我！",
            "呜呜",
            "这是一条随机回复",
            "在！",
            at_back + " 是真的欠了",
            at_back + " 干嘛……",
            "再戳要坏掉了！",
            "哼",
            "awa",
            "qaq",
            "李在赣神魔！",
            UniMessage.image(path=Path("./res/干嘛.jpg")),
            "干嘛。。。",
            "呀！",
            UniMessage.image(path=Path("./res/小镜指.jpg")),
            "呼呼！",
            "哼哼！",
            "不要乱戳哦！",
            "好哦！",
            UniMessage.emoji(id="86").emoji(id="86").emoji(id="86"),
            at_back.text(" ").emoji(id="181").emoji(id="181"),
        )
        + _special
    )

    if group is None:
        await send_private_msg(bot, sender, message)
    else:
        await send_group_msg(bot, group, message)


LAST_POKE_TIME: dict[int, float] = {}


@root.listen(GroupPokeContext)
async def _(ctx: GroupPokeContext):
    if ctx.event.target_id == ctx.event.self_id:
        last = LAST_POKE_TIME.get(ctx.event.user_id, 0.0)
        curr = time.time()
        if curr - last < 1:
            return
        LAST_POKE_TIME[ctx.event.user_id] = curr
        await reply_call(
            ctx.bot,
            ctx.event.group_id,
            ctx.event.user_id,
            await get_name(ctx.bot, ctx.event.user_id, ctx.event.group_id),
        )


@listen_message()
@require_awake
async def _(ctx: GroupContext):
    if len(ctx.message) != 1:
        return

    message = ctx.message[0]
    if not isinstance(message, At):
        return

    if message.target == ctx.bot.self_id:
        await reply_call(
            ctx.bot,
            ctx.group_id,
            ctx.sender_id,
            await ctx.sender_name,
        )

        if get_random().random() < 0.1:
            await ctx.stickEmoji(QQEmoji.跳跳)
