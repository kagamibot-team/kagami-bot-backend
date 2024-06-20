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

    async def getMessage(self) -> UniMessage[Segment]:
        # return cast(UniMessage[Any], self.event.get_message())
        return cast(
            UniMessage[Segment],
            await UniMessage.generate(event=self.event, bot=self.bot),
        )

    async def getText(self) -> str:
        return (await self.getMessage()).extract_plain_text()

    async def send(self, message: UniMessage[Any] | str):
        if isinstance(message, str):
            message = UniMessage(message)

        return await message.send(
            target=self.event,
            bot=self.bot,
        )

    async def reply(self, message: UniMessage[Any] | str):
        return await self.send(message)

    async def isTextOnly(self) -> bool:
        return (await self.getMessage()).only(Text)


class GroupContext(UniContext[GroupMessageEvent, _OnebotBot]):
    def getSenderId(self):
        return self.event.user_id

    async def getSenderNameInGroup(self):
        sender = self.getSenderId()
        info = await self.bot.get_group_member_info(
            group_id=self.event.group_id, user_id=sender
        )
        name: str = info["nickname"]
        name = info["card"] or name
        return name

    async def getSenderName(self):
        return await self.getSenderNameInGroup()

    async def reply(self, message: UniMessage[Any] | str):
        return await self.send((UniMessage.at(str(self.getSenderId())) + " " + message))


class PrivateContext(UniContext[PrivateMessageEvent, _OnebotBot]):
    def getSenderId(self):
        return self.event.user_id

    async def getSenderName(self) -> str:
        info = await self.bot.get_stranger_info(user_id=self.getSenderId())
        return info["nick"]


class ConsoleContext(UniContext[_ConsoleEvent, _ConsoleBot]):
    def getSenderId(self):
        return None


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
