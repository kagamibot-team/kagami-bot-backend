from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Iterable, Sequence, TypeVar, cast

from nonebot.adapters.console.event import MessageEvent as _ConsoleEvent
from nonebot.adapters.console.bot import Bot as _ConsoleBot
from nonebot.adapters.console import Message as _ConsoleMessage

from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot as _OnebotBot

from nonebot_plugin_alconna.uniseg.message import UniMessage, Receipt
from nonebot_plugin_alconna import Segment, Text
from nonebot.adapters import Event, Bot


TE = TypeVar("TE", bound=Event)
TB = TypeVar("TB", bound=Bot)
TS = TypeVar("TS", bound=Segment)

TRECEIPT = TypeVar("TRECEIPT")

TONEBOTEVENT = TypeVar("TONEBOTEVENT", bound=GroupMessageEvent | PrivateMessageEvent)


class Context(ABC, Generic[TRECEIPT]):
    @abstractmethod
    async def getMessage(self) -> Sequence[Any]: ...

    @abstractmethod
    async def send(self, message: Sequence[Any] | str) -> TRECEIPT: ...

    @abstractmethod
    async def reply(self, message: Sequence[Any] | str) -> TRECEIPT: ...

    @abstractmethod
    def getSenderId(self) -> int | None: ...

    @abstractmethod
    async def getText(self) -> str: ...

    @abstractmethod
    async def isTextOnly(self) -> bool: ...


class UniMessageContext(Context[Receipt]):
    @abstractmethod
    async def getMessage(self) -> UniMessage[Any]: ...

    @abstractmethod
    async def send(self, message: Iterable[Any] | str) -> Receipt: ...

    @abstractmethod
    async def reply(self, message: Iterable[Any] | str) -> Receipt: ...

    async def getText(self) -> str:
        return (await self.getMessage()).extract_plain_text()

    async def isTextOnly(self) -> bool:
        return (await self.getMessage()).only(Text)


@dataclass
class UniContext(UniMessageContext, Generic[TE, TB]):
    event: TE
    bot: TB

    async def getMessage(self) -> UniMessage[Any]:
        return cast(
            UniMessage[Any],
            await UniMessage.generate(event=self.event, bot=self.bot),  # type: ignore
        )

    async def send(self, message: Iterable[Any] | str):
        message = UniMessage(message)

        return await message.send(
            target=self.event,
            bot=self.bot,
        )

    async def reply(self, message: Iterable[Any] | str):
        return await self.send(message)


class OnebotContext(UniContext[TONEBOTEVENT, _OnebotBot]):
    def getSenderId(self):
        return self.event.user_id

    async def getSenderName(self) -> str:
        info = await self.bot.get_stranger_info(user_id=self.getSenderId())
        return info["nick"]


class GroupContext(OnebotContext[GroupMessageEvent]):
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

    async def reply(self, message: Iterable[Any] | str):
        return await self.send(
            cast(
                UniMessage[Any], UniMessage.at(str(self.getSenderId())) + " " + message
            )
        )


class PrivateContext(OnebotContext[PrivateMessageEvent]):
    pass


@dataclass
class ConsoleContext(Context[None]):
    event: _ConsoleEvent
    bot: _ConsoleBot

    async def getMessage(self) -> list[str]:
        return [str(s) for s in self.event.message]

    async def send(self, message: Sequence[Any] | str) -> None:
        return await self.bot.send_msg(
            user_id="", message=_ConsoleMessage("".join([str(a) for a in message]))
        )

    async def reply(self, message: Sequence[Any] | str) -> None:
        return await self.send(message)

    async def getText(self) -> str:
        return self.event.message.extract_plain_text()

    async def isTextOnly(self) -> bool:
        return True

    def getSenderId(self):
        return None


# FALLBACK
PublicContext = Context


__all__ = [
    "UniContext",
    "GroupContext",
    "PrivateContext",
    "ConsoleContext",
    "OnebotContext",
    "Context",
    "UniMessageContext",
    "PublicContext",
]
