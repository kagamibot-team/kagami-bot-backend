from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

from nonebot import logger
from nonebot.adapters.console.event import MessageEvent as _ConsoleEvent
from nonebot.adapters.console.bot import Bot as _ConsoleBot

from nonebot.adapters.onebot.v11 import GroupMessageEvent as _OneBotGroupMessageEvent
from nonebot.adapters.onebot.v11 import (
    PrivateMessageEvent as _OneBotPrivateMessageEvent,
)
from nonebot.adapters.onebot.v11 import MessageEvent as _OneBotMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot as _OnebotBot

from nonebot_plugin_alconna.uniseg.message import UniMessage
from nonebot_plugin_alconna import Segment, At, Text
from nonebot.adapters import Event, Bot

from arclet.alconna.typing import TDC


TE = TypeVar("TE", bound=Event)
TB = TypeVar("TB", bound=Bot)
TS = TypeVar("TS", bound=Segment)


class Context(Generic[TE, TDC]):
    event: TE

    def getMessage(self) -> TDC:
        return cast(TDC, self.event.get_message())

    def getText(self) -> str:
        return self.event.get_message().extract_plain_text()
    
    def isTextOnly(self) -> bool:
        raise NotImplementedError


@dataclass
class UniContext(Generic[TE, TB], Context[TE, UniMessage[Any]]):
    event: TE
    bot: TB

    async def send(self, message: UniMessage[Any]):
        return await message.send(
            target=self.event,
            bot=self.bot,
        )

    async def reply(self, message: UniMessage[Any]):
        return await self.send(message)
    
    def isTextOnly(self) -> bool:
        return self.getMessage().only(Text)


class OnebotGroupContext(UniContext[_OneBotGroupMessageEvent, _OnebotBot]):
    def getSenderId(self):
        return self.event.user_id

    async def reply(self, message: UniMessage[Any]):
        return await self.send((UniMessage.at(str(self.getSenderId())) + " " + message))


class OnebotPrivateContext(UniContext[_OneBotPrivateMessageEvent, _OnebotBot]):
    def getSenderId(self):
        return self.event.user_id

    async def reply(self, message: UniMessage[Any]):
        return await self.send(message)


class ConsoleContext(UniContext[_ConsoleEvent, _ConsoleBot]):
    def getSenderId(self):
        return None

    async def reply(self, message: UniMessage[Any]):
        return await self.send(message)


OnebotContext = OnebotGroupContext | OnebotPrivateContext


PublicContext = (
    OnebotGroupContext | OnebotPrivateContext | ConsoleContext
)
