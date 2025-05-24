from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Any,
    Generic,
    Iterable,
    TypeVar,
    cast,
)

from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    GroupMessageEvent,
)
from nonebot_plugin_alconna import Segment, Text, get_message_id
from nonebot_plugin_alconna.uniseg.adapters import BUILDER_MAPPING  # type: ignore
from nonebot_plugin_alconna.uniseg.message import UniMessage

from src.base.onebot.onebot_api import (
    send_group_msg,
    set_msg_emoji_like,
)
from src.base.onebot.onebot_basic import (
    MessageLike,
    OnebotBotProtocol,
    export_msg,
)
from src.base.onebot.onebot_enum import QQEmoji
from src.base.onebot.onebot_tools import get_name_cached


TE = TypeVar("TE", bound="MessageEvent")


class MessageContext(ABC):
    @property
    @abstractmethod
    def sender_id(self) -> int: ...

    @abstractmethod
    async def send(self, message: UniMessage[Any] | str) -> Any: ...

    @abstractmethod
    async def reply(
        self,
        message: UniMessage[Any] | str,
        ref: bool = False,
        at: bool = True,
    ) -> Any: ...

    @abstractmethod
    async def get_sender_name(self) -> str: ...

    @property
    @abstractmethod
    def message(self) -> UniMessage[Segment]: ...

    @property
    def sender_name(self):
        return self.get_sender_name()

    def is_text_only(self) -> bool:
        return self.message.only(Text)

    @property
    def text(self):
        return self.message.extract_plain_text()

    async def send_image(self, image: Path | bytes):
        if isinstance(image, Path):
            image = image.read_bytes()
        msg = UniMessage.image(raw=image)
        return await self.send(msg)


class OnebotContext(MessageContext, Generic[TE]):
    event: TE
    bot: OnebotBotProtocol

    @property
    def group_id(self) -> int | None:
        return None

    def __init__(self, event: TE, bot: OnebotBotProtocol) -> None:
        self.event = event
        self.bot = bot

    @abstractmethod
    async def _send(self, message: MessageLike) -> Any: ...

    @property
    def message(self) -> UniMessage[Segment]:
        return cast(
            UniMessage[Segment],
            UniMessage(BUILDER_MAPPING["OneBot V11"].generate(self.event.original_message)),  # type: ignore
        )

    async def reply(
        self,
        message: Iterable[Any] | str,
        ref: bool = False,
        at: bool = True,
    ) -> Any:
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
            msg = UniMessage.at(str(self.sender_id)) + " " + msg
        if ref:
            msg = UniMessage.reply(get_message_id(self.event)) + msg
        return await self.send(msg)

    @property
    def sender_id(self):
        return self.event.user_id

    async def get_sender_name(self) -> str:
        # return await get_name(self.bot, self.sender_id, None)
        return await get_name_cached(None, self.sender_id, self.bot)

    async def send(self, message: Iterable[Any] | str):
        message = UniMessage(message)
        msg_out = export_msg(message)
        await self._send(message=msg_out)


class GroupContext(OnebotContext[GroupMessageEvent]):
    @property
    def group_id(self):
        return self.event.group_id

    async def get_sender_name(self):
        # return await get_name(self.bot, self.sender_id, self.group_id)
        return await get_name_cached(self.group_id, self.sender_id, self.bot)

    async def _send(self, message: MessageLike):
        return await send_group_msg(self.bot, self.event.group_id, message)

    async def stickEmoji(self, emoji_id: int | str | QQEmoji):
        """贴表情。该接口仅在群聊中可用。

        Args:
            emoji_id (int | str | QQEmoji): 表情的 ID，参见[相关文档](https://bot.q.qq.com/wiki/develop/api-v2/openapi/emoji/model.html#EmojiType)
        """

        await set_msg_emoji_like(self.bot, get_message_id(self.event), emoji_id)

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


__all__ = [
    "GroupContext",
]
