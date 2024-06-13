from nonebot import on_type
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.console import Bot as ConsoleBot
from nonebot.adapters.console import MessageEvent as ConsoleMessageEvent

from .manager import EventManager
from .context import (
    ConsoleMessageContext,
    OnebotGroupMessageContext,
    OnebotPrivateMessageContext,
)


def activateRoot(root: EventManager):
    consoleHandler = on_type(ConsoleMessageEvent)
    groupMessageHandler = on_type(GroupMessageEvent)
    privateMessageHandler = on_type(PrivateMessageEvent)


    @consoleHandler.handle()
    async def _(bot: ConsoleBot, event: ConsoleMessageEvent):
        await root.emit(ConsoleMessageContext(event, bot))


    @groupMessageHandler.handle()
    async def _(bot: Bot, event: GroupMessageEvent):
        await root.emit(OnebotGroupMessageContext(event, bot))


    @privateMessageHandler.handle()
    async def _(bot: Bot, event: PrivateMessageEvent):
        await root.emit(OnebotPrivateMessageContext(event, bot))


root = EventManager()
