from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Iterable, Protocol, Sequence, TypeVar, cast

from nonebot.adapters.console.event import MessageEvent as _ConsoleEvent
from nonebot.adapters.console.bot import Bot as _ConsoleBot
from nonebot.adapters import Message

from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot as _OnebotBot

from nonebot_plugin_alconna.uniseg.message import UniMessage
from nonebot_plugin_alconna.uniseg.adapters import EXPORTER_MAPPING, BUILDER_MAPPING
from nonebot_plugin_alconna import Segment, Text


class Recallable(Protocol):
    async def recall(self, *args: Any, **kwargs: Any) -> Any: ...


class NoRecall(Recallable):
    async def recall(self) -> None:
        return None


class OnebotEventProtocol(Protocol):
    user_id: int
    to_me: bool

    def get_message(self) -> Message[Any]: ...


class OnebotGroupEventProtocol(OnebotEventProtocol, Protocol):
    group_id: int


class __:
    user_id: int = 1
    group_id: int = 2


TRECEIPT = TypeVar("TRECEIPT")
TE = TypeVar("TE", bound="OnebotEventProtocol")


@dataclass
class OnebotReceipt:
    bot: _OnebotBot
    message_id: int

    async def recall(self):
        await self.bot.delete_msg(message_id=self.message_id)


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


class UniMessageContext(Context[TRECEIPT], Generic[TRECEIPT]):
    @abstractmethod
    async def getMessage(self) -> UniMessage[Segment]: ...

    @abstractmethod
    async def send(self, message: Iterable[Any] | str) -> TRECEIPT: ...

    @abstractmethod
    async def reply(self, message: Iterable[Any] | str) -> TRECEIPT: ...

    async def getText(self) -> str:
        return (await self.getMessage()).extract_plain_text()

    async def isTextOnly(self) -> bool:
        return (await self.getMessage()).only(Text)


@dataclass
class OnebotContext(UniMessageContext[OnebotReceipt], Generic[TE]):
    event: TE
    bot: _OnebotBot

    async def getMessage(self) -> UniMessage[Segment]:
        return cast(
            UniMessage[Segment],
            UniMessage(BUILDER_MAPPING["OneBot V11"].generate(self.event.get_message())),  # type: ignore
        )

    async def reply(self, message: Iterable[Any] | str):
        return await self.send(message)

    def getSenderId(self):
        return self.event.user_id

    async def getSenderName(self) -> str:
        info = await self.bot.get_stranger_info(user_id=self.getSenderId())
        return info["nick"]


class GroupContext(OnebotContext[OnebotGroupEventProtocol]):
    async def getSenderNameInGroup(self):
        sender = self.getSenderId()
        info = await self.bot.get_group_member_info(
            group_id=self.event.group_id, user_id=sender
        )
        name: str = info["nickname"]
        name = info["card"] or name
        return name

    async def send(self, message: Iterable[Any] | str) -> OnebotReceipt:
        message = UniMessage(message)
        msg_out = await EXPORTER_MAPPING["OneBot V11"].export(message, self.bot, False)
        msg_info = await self.bot.send_group_msg(
            group_id=self.event.group_id, message=msg_out
        )

        return OnebotReceipt(self.bot, msg_info["message_id"])

    async def reply(self, message: Iterable[Any] | str):
        return await self.send(
            cast(
                UniMessage[Any], UniMessage.at(str(self.getSenderId())) + " " + message
            )
        )

    async def is_group_admin(self) -> bool:
        """判断自己是不是这个群的管理员

        Returns:
            bool: 是否是管理员
        """

        info = await self.bot.get_group_member_info(
            group_id=self.event.group_id, user_id=int(self.bot.self_id)
        )

        return info["role"] == "admin" or info["role"] == "owner"


class PrivateContext(OnebotContext[OnebotEventProtocol]):
    async def send(self, message: Iterable[Any] | str) -> OnebotReceipt:
        message = UniMessage(message)
        msg_out = await EXPORTER_MAPPING["OneBot V11"].export(message, self.bot, False)
        msg_info = await self.bot.send_private_msg(
            user_id=self.event.user_id, message=msg_out
        )

        return OnebotReceipt(self.bot, msg_info["message_id"])


@dataclass
class ConsoleContext(UniMessageContext):
    event: _ConsoleEvent
    bot: _ConsoleBot

    async def send(self, message: Iterable[Any] | str):
        await self.bot.send(self.event, str(message))
        return NoRecall()

    async def reply(self, message: Iterable[Any] | str):
        return await self.send(message)

    def getSenderId(self):
        return None

    async def getMessage(self) -> UniMessage[Any]:
        return UniMessage(self.event.message.extract_plain_text())


# FALLBACK
PublicContext = UniMessageContext


__all__ = [
    "GroupContext",
    "PrivateContext",
    "ConsoleContext",
    "OnebotContext",
    "Context",
    "UniMessageContext",
    "PublicContext",
]
