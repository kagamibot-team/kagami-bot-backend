from abc import ABC, abstractmethod
from typing import (
    Any,
    Generic,
    Iterable,
    Literal,
    NotRequired,
    Sequence,
    TypedDict,
    TypeVar,
    cast,
)

from nonebot.adapters.console.bot import Bot as _ConsoleBot
from nonebot.adapters.console.event import MessageEvent as _ConsoleEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_alconna import Segment, Text
from nonebot_plugin_alconna.uniseg.adapters import BUILDER_MAPPING # type: ignore
from nonebot_plugin_alconna.uniseg.message import UniMessage

from src.base.onebot_api import (
    delete_msg,
    send_group_msg,
    send_private_msg,
    set_msg_emoji_like,
)
from src.base.onebot_basic import (
    MessageLike,
    NoRecall,
    OnebotBotProtocol,
    OnebotEventProtocol,
    OnebotGroupEventProtocol,
    Recallable,
    export_msg,
)
from src.base.onebot_enum import QQEmoji


class _ForwardMessageData(TypedDict):
    id: NotRequired[int]
    name: NotRequired[str]
    uin: NotRequired[str]
    content: NotRequired[Message]
    seq: NotRequired[str]


class _ForwardMessageNode(TypedDict):
    type: Literal["node"]
    data: _ForwardMessageData


def forwardMessage(
    content: Message | str | Iterable[Any], name: str = "", uin: int | str = ""
) -> _ForwardMessageData:
    """构造转发消息

    Args:
        name (str): 发送者应该呈现的名字
        uin (int | str): 发送者的 QQ 号，用于识别是否为好友等
        content (Message): 消息内容
    """

    if isinstance(content, dict):
        if set(content.keys()) == {"name", "uin", "content"}:
            if (
                isinstance(content["name"], str)
                and isinstance(content["uin"], str)
                and isinstance(content["content"], Message)
            ):
                return cast(_ForwardMessageData, content)

    if isinstance(content, str):
        content = Message(MessageSegment.text(content))
    elif isinstance(content, UniMessage):
        content = export_msg(content)
    elif isinstance(content, Message):
        pass
    else:
        raise ValueError(
            f"暂时不支持处理 {content}，如果遇到这个错误，请联系 Passthem。"
        )

    return {"name": name, "uin": str(uin), "content": content}


TRECEIPT = TypeVar("TRECEIPT", bound=Recallable)
TE = TypeVar("TE", bound="OnebotEventProtocol")


class OnebotReceipt:
    bot: OnebotBotProtocol
    message_id: int

    def __init__(self, bot: OnebotBotProtocol, message_id: int) -> None:
        self.bot = bot
        self.message_id = message_id

    async def recall(self):
        await delete_msg(self.bot, self.message_id)


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


class UniMessageContext(Context[Recallable]):
    @abstractmethod
    async def getMessage(self) -> UniMessage[Segment]: ...

    @abstractmethod
    async def send(self, message: Iterable[Any] | str) -> Recallable: ...

    @abstractmethod
    async def reply(self, message: Iterable[Any] | str) -> Recallable: ...

    async def getText(self) -> str:
        return (await self.getMessage()).extract_plain_text()

    async def isTextOnly(self) -> bool:
        return (await self.getMessage()).only(Text)


class OnebotMessageContext(UniMessageContext, Generic[TE]):
    event: TE
    bot: OnebotBotProtocol

    def __init__(self, event: TE, bot: OnebotBotProtocol) -> None:
        self.event = event
        self.bot = bot

    @abstractmethod
    async def _send(self, message: MessageLike) -> Any: ...

    @abstractmethod
    async def _send_forward(self, messages: list[_ForwardMessageNode]) -> Any: ...

    async def getMessage(self) -> UniMessage[Segment]:
        return cast(
            UniMessage[Segment],
            UniMessage(BUILDER_MAPPING["OneBot V11"].generate(self.event.get_message())),  # type: ignore
        )

    async def reply(
        self,
        message: Iterable[Any] | str,
        ref: bool = False,
        at: bool = True,
    ):
        """回复从 Context 来的消息

        Args:
            message (Iterable[Any] | str): 发送的消息。
            ref (bool, optional): 是否要引用原消息，默认为 False。
            at (bool, optional): 是否要 at 发送者，默认为 True。

        Returns:
            Any: 调用发送消息接口时返回的 JSON 字典，具体需要查阅 Onebot V11 文档
        """
        msg = message
        if at:
            msg = UniMessage.at(str(self.getSenderId())) + " " + msg
        if ref:
            msg = UniMessage.reply((await self.getMessage()).get_message_id()) + msg
        return await self.send(msg)

    def getSenderId(self):
        return self.event.user_id

    async def getSenderName(self) -> str:
        info = await self.bot.call_api("get_stranger_info", user_id=self.getSenderId())
        return info["nick"]

    async def send(self, message: Iterable[Any] | str) -> OnebotReceipt:
        message = UniMessage(message)
        msg_out = export_msg(message)
        msg_info = await self._send(message=msg_out)

        return OnebotReceipt(self.bot, msg_info["message_id"])

    async def sendCompact(
        self, *messages: _ForwardMessageData | Message | str | Iterable[Any]
    ):
        """合并转发消息。直接往这个函数里面输入需要合并转发的消息就好了。例如：

        ```python
        await ctx.sendCompact("消息1", "消息2")
        await ctx.sendCompact(
            UniMessage().image(...).text("这里是我的一些话"),
            "还有呢……"
        )
        ```

        不知道为什么，这个接口发送消息的速度不是很快。

        Returns:
            Any: 根据 Go-CQHTTP API 协议返回的内容，详见 https://docs.go-cqhttp.org/api/
        """

        nodes: list[_ForwardMessageNode] = []

        for message in messages:
            if isinstance(message, (str, dict)):
                message = forwardMessage(message)
                nodes.append({"type": "node", "data": message})
            else:
                if isinstance(message, UniMessage):
                    message = export_msg(message)
                elif isinstance(message, Message):
                    pass
                else:
                    raise Exception(
                        f"暂时不支持处理 {message}，请联系 Passthem 添加对这种消息的支持"
                    )

                info = await self.bot.call_api(
                    "send_private_msg", user_id=self.bot.self_id, message=message
                )
                message_id = info["message_id"]
                rid_info = await self.bot.call_api("get_msg", message_id=message_id)

                nodes.append({"data": {"id": int(rid_info["real_id"])}, "type": "node"})

        return await self._send_forward(nodes)


class GroupContext(OnebotMessageContext[OnebotGroupEventProtocol]):
    async def getSenderName(self):
        sender = self.getSenderId()
        info = await self.bot.call_api(
            "get_group_member_info", group_id=self.event.group_id, user_id=sender
        )
        name: str = info["nickname"]
        name = info["card"] or name
        return name

    async def _send(self, message: MessageLike):
        return await send_group_msg(self.bot, self.event.group_id, message)

    async def _send_forward(self, messages: list[_ForwardMessageNode]) -> Any:
        return await self.bot.call_api(
            "send_group_forward_msg", group_id=self.event.group_id, messages=messages
        )

    async def stickEmoji(self, emoji_id: int | str | QQEmoji):
        """贴表情。该接口仅在群聊中可用。

        Args:
            emoji_id (int | str | QQEmoji): 表情的 ID，参见[相关文档](https://bot.q.qq.com/wiki/develop/api-v2/openapi/emoji/model.html#EmojiType)
        """

        await set_msg_emoji_like(
            self.bot, int((await self.getMessage()).get_message_id()), emoji_id
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


class PrivateContext(OnebotMessageContext[OnebotEventProtocol]):
    async def _send(self, message: MessageLike):
        return await send_private_msg(self.bot, self.event.user_id, message)

    async def _send_forward(self, messages: list[_ForwardMessageNode]) -> Any:
        return await self.bot.call_api(
            "send_private_forward_msg", group_id=self.event.user_id, messages=messages
        )


class ConsoleContext(UniMessageContext):
    event: _ConsoleEvent
    bot: _ConsoleBot

    def __init__(self, event: _ConsoleEvent, bot: _ConsoleBot) -> None:
        self.event = event
        self.bot = bot

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
    "OnebotMessageContext",
    "Context",
    "UniMessageContext",
    "PublicContext",
    "forwardMessage",
]
