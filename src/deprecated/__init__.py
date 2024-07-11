"""
所有在 Onebot V11 协议下的指令
"""

from src.base.db import get_session
from .old_version import CommandBase
from nonebot import on_type
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from typing import NoReturn


from .old_version import (
    CheckEnvironment,
)

from .admin import (
    Give,
    CatchAddSkin,
    CatchGiveMoney,
    AddAltName,
    RemoveAltName,
    AddTags,
    RemoveTags,
)


enabledCommand: list[CommandBase] = [
    Give(),
    CatchAddSkin(),
    CatchGiveMoney(),
    AddAltName(),
    RemoveAltName(),
    AddTags(),
    RemoveTags(),
]


eventMatcher = on_type(types=GroupMessageEvent)


async def finish(message: Message) -> NoReturn:
    await eventMatcher.finish(message)


@eventMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    sender = event.sender.user_id
    session = get_session()
    async with session.begin():
        if sender is None:
            return
        assert isinstance(sender, int)

        text = event.get_plaintext()

        env = CheckEnvironment(
            sender, text, event.message_id, event.message, session, bot, event.group_id
        )

        for command in enabledCommand:
            message = await command.check(env)

            if message:
                await finish(message)
