from nonebot import on_type
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import FinishedException
from typing import Callable, Coroutine, NoReturn


from .putils.command import (
    CallbackBase,
    CheckEnvironment,
    WaitForMoreInformationException,
)

from .commands import enabledCommand

from nonebot_plugin_orm import async_scoped_session


eventMatcher = on_type(types=GroupMessageEvent)


async def finish(message: Message) -> NoReturn:
    await eventMatcher.finish(message)


callbacks: dict[int, CallbackBase | None] = {}


def getCallbacks(uid: int):
    if uid not in callbacks.keys():
        callbacks[uid] = None

    return callbacks[uid]


def save_on_finish(fn: Callable[[async_scoped_session, Bot, GroupMessageEvent], Coroutine[None, None, None]]):
    async def wrapper(session: async_scoped_session, bot: Bot, event: GroupMessageEvent):
        try:
            await fn(session, bot, event)
        finally:
            await session.commit()

    return wrapper


@eventMatcher.handle()
@save_on_finish
async def _(session: async_scoped_session, bot: Bot, event: GroupMessageEvent):
    sender = event.sender.user_id

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
