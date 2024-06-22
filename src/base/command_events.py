from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Iterable, Protocol, Sequence, TypeVar, cast

from nonebot.adapters.console.event import MessageEvent as _ConsoleEvent
from nonebot.adapters.console.bot import Bot as _ConsoleBot
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from nonebot_plugin_alconna.uniseg.message import UniMessage
from nonebot_plugin_alconna.uniseg.adapters import BUILDER_MAPPING
from nonebot_plugin_alconna import Segment, Image, Text, At, Emoji


class Recallable(Protocol):
    async def recall(self, *args: Any, **kwargs: Any) -> Any: ...


class NoRecall(Recallable):
    async def recall(self) -> None:
        return None


class OnebotEventProtocol(Protocol):
    user_id: int
    to_me: bool

    def get_message(self) -> Message: ...


class OnebotGroupEventProtocol(OnebotEventProtocol, Protocol):
    group_id: int


class OnebotBotProtocol(Protocol):
    self_id: str

    async def call_api(self, api: str, **data: Any) -> Any: ...


def export_msg(msg: UniMessage[Any]) -> Message:
    result = Message()

    for seg in msg:
        if isinstance(seg, Text):
            result.append(MessageSegment.text(seg.text))
        elif isinstance(seg, Image):
            if seg.raw is not None:
                result.append(MessageSegment.image(file=seg.raw))
            elif seg.path is not None:
                result.append(MessageSegment.image(file=seg.path))
            else:
                raise Exception("需要输出的 Image 节点请指定其 raw 或 path 属性")
        elif isinstance(seg, At):
            result.append(MessageSegment.at(seg.target))
        elif isinstance(seg, Emoji):
            result.append(MessageSegment.face(int(seg.id)))
        else:
            raise Exception(f"暂时不支持处理 {seg}，请联系 Passthem 添加对这种消息的支持")

    return result


TRECEIPT = TypeVar("TRECEIPT")
TE = TypeVar("TE", bound="OnebotEventProtocol")


@dataclass
class OnebotReceipt:
    bot: OnebotBotProtocol
    message_id: int

    async def recall(self):
        await self.bot.call_api("delete_msg", message_id=self.message_id)


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
    bot: OnebotBotProtocol

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
        info = await self.bot.call_api("get_stranger_info", user_id=self.getSenderId())
        return info["nick"]


class GroupContext(OnebotContext[OnebotGroupEventProtocol]):
    async def getSenderNameInGroup(self):
        sender = self.getSenderId()
        info = await self.bot.call_api(
            "get_group_member_info", group_id=self.event.group_id, user_id=sender
        )
        name: str = info["nickname"]
        name = info["card"] or name
        return name

    async def send(self, message: Iterable[Any] | str) -> OnebotReceipt:
        message = UniMessage(message)
        msg_out = export_msg(message)
        msg_info = await self.bot.call_api(
            "send_group_msg", group_id=self.event.group_id, message=msg_out
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

        info = await self.bot.call_api(
            "get_group_member_info",
            group_id=self.event.group_id,
            user_id=int(self.bot.self_id),
        )

        return info["role"] == "admin" or info["role"] == "owner"


class PrivateContext(OnebotContext[OnebotEventProtocol]):
    async def send(self, message: Iterable[Any] | str) -> OnebotReceipt:
        message = UniMessage(message)
        msg_out = export_msg(message)
        msg_info = await self.bot.call_api(
            "send_private_msg", user_id=self.event.user_id, message=msg_out
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
