from nonebot import on_type
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.console import Bot as ConsoleBot
from nonebot.adapters.console import MessageEvent as ConsoleMessageEvent

from .manager import EventManager
from .context import (
    ConsoleContext,
    OnebotGroupContext,
    OnebotPrivateContext,
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
        await root.throw(OnebotGroupContext(event, bot))


    @privateMessageHandler.handle()
    async def _(bot: Bot, event: PrivateMessageEvent):
        await root.throw(OnebotPrivateContext(event, bot))


root = EventManager()
