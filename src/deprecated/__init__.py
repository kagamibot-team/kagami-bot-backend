"""
所有在 Onebot V11 协议下的指令
"""


from src.base.db import get_session
from .old_version import CommandBase
from nonebot import on_type
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import FinishedException
from typing import NoReturn


from .old_version import (
    CallbackBase,
    CheckEnvironment,
    WaitForMoreInformationException,
)


from .basics import (
    CatchShop,
)

from .admin import (
    CatchAllLevel,
    CatchSetInterval,
    CatchLevelModify,
    CatchCreateLevel,
    Give,
    Clear,
    CatchAddSkin,
    CatchAdminDisplay,
    CatchAdminObtainSkin,
    CatchAdminDeleteSkinOwnership,
    CatchResetEveryoneCacheCount,
    CatchGiveMoney,
    AddAltName,
    RemoveAltName,
    AddTags,
    RemoveTags,
)


enabledCommand: list[CommandBase] = [
    CatchAllLevel(),
    CatchSetInterval(),
    CatchLevelModify(),
    CatchCreateLevel(),
    Give(),
    Clear(),
    CatchAddSkin(),
    CatchAdminDisplay(),
    CatchAdminObtainSkin(),
    CatchAdminDeleteSkinOwnership(),
    CatchShop(),
    CatchResetEveryoneCacheCount(),
    CatchGiveMoney(),
    AddAltName(),
    RemoveAltName(),
    AddTags(),
    RemoveTags(),
]


eventMatcher = on_type(types=GroupMessageEvent)


async def finish(message: Message) -> NoReturn:
    await eventMatcher.finish(message)


callbacks: dict[int, CallbackBase | None] = {}


def getCallbacks(uid: int):
    if uid not in callbacks.keys():
        callbacks[uid] = None

    return callbacks[uid]


@eventMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    sender = event.sender.user_id
    session = get_session()
    async with session.begin():
        if sender == None:
            return
        assert type(sender) == int

        text = event.get_plaintext()

        env = CheckEnvironment(sender, text, event.message_id, event.message, session, bot, event.group_id)

        callback = getCallbacks(sender)
        if callback != None:
            try:
                message = await callback.check(env)
            except WaitForMoreInformationException as e:
                callbacks[sender] = e.callback
                if e.message is not None:
                    await finish(e.message)
                raise FinishedException()
            finally:
                await session.commit()

            callbacks[sender] = None

            if message:
                await finish(message)

            raise FinishedException()

        for command in enabledCommand:
            try:
                message = await command.check(env)
            except WaitForMoreInformationException as e:
                callbacks[sender] = e.callback
                if e.message is not None:
                    await finish(e.message)
                raise FinishedException()

            if message:
                await finish(message)
