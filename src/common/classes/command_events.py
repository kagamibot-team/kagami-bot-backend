from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

from nonebot.adapters.console.event import MessageEvent as _ConsoleEvent
from nonebot.adapters.console.bot import Bot as _ConsoleBot

from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot as _OnebotBot

from nonebot_plugin_alconna.uniseg.message import UniMessage
from nonebot_plugin_alconna import Segment, Text
from nonebot.adapters import Event, Bot


TE = TypeVar("TE", bound=Event)
TB = TypeVar("TB", bound=Bot)
TS = TypeVar("TS", bound=Segment)


@dataclass
class UniContext(Generic[TE, TB]):
    event: TE
    bot: TB

    async def getMessage(self) -> UniMessage[Any]:
        # return cast(UniMessage[Any], self.event.get_message())
        return cast(UniMessage, await UniMessage.generate(event=self.event, bot=self.bot))

    async def getText(self) -> str:
        return (await self.getMessage()).extract_plain_text()

    async def send(self, message: UniMessage[Any]):
        return await message.send(
            target=self.event,
            bot=self.bot,
        )

    async def reply(self, message: UniMessage[Any]):
        return await self.send(message)

    async def isTextOnly(self) -> bool:
        return (await self.getMessage()).only(Text)


class GroupContext(UniContext[GroupMessageEvent, _OnebotBot]):
    def getSenderId(self):
        return self.event.user_id

    async def reply(self, message: UniMessage[Any]):
        return await self.send((UniMessage.at(str(self.getSenderId())) + " " + message))


class PrivateContext(UniContext[PrivateMessageEvent, _OnebotBot]):
    def getSenderId(self):
        return self.event.user_id

    async def reply(self, message: UniMessage[Any]):
        return await self.send(message)


class ConsoleContext(UniContext[_ConsoleEvent, _ConsoleBot]):
    def getSenderId(self):
        return None

    async def reply(self, message: UniMessage[Any]):
        return await self.send(message)


OnebotContext = GroupContext | PrivateContext


PublicContext = GroupContext | PrivateContext | ConsoleContext


__all__ = [
    "UniContext",
    "GroupContext",
    "PrivateContext",
    "ConsoleContext",
    "OnebotContext",
    "PublicContext",
]
