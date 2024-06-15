from nonebot import on_type
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.console import Bot as ConsoleBot
from nonebot.adapters.console import MessageEvent as ConsoleMessageEvent

from src.common.classes.event_manager import EventManager
from .classes.command_events import (
    ConsoleContext,
    GroupContext,
    PrivateContext,
)


def activateRoot(root: EventManager):
    consoleHandler = on_type(ConsoleMessageEvent)
    groupMessageHandler = on_type(GroupMessageEvent)
    privateMessageHandler = on_type(PrivateMessageEvent)


    @consoleHandler.handle()
    async def _(bot: ConsoleBot, event: ConsoleMessageEvent):
        await root.throw(ConsoleContext(event, bot))


    @groupMessageHandler.handle()
    async def _(bot: Bot, event: GroupMessageEvent):
        await root.throw(GroupContext(event, bot))


    @privateMessageHandler.handle()
    async def _(bot: Bot, event: PrivateMessageEvent):
        await root.throw(PrivateContext(event, bot))


root = EventManager()


__all__ = ["root", "activateRoot"]
