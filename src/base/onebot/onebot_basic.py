from typing import Any, Protocol, cast

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_alconna.uniseg.message import UniMessage


class Recallable(Protocol):
    async def recall(self, *args: Any, **kwargs: Any) -> Any: ...


class NoRecall(Recallable):
    async def recall(self, *args: Any, **kwargs: Any) -> None:
        return None


class OnebotEventProtocol(Protocol):
    user_id: int
    to_me: bool
    original_message: Message

    def get_message(self) -> Message: ...


class OnebotGroupEventProtocol(OnebotEventProtocol, Protocol):
    group_id: int


class OnebotBotProtocol(Protocol):
    self_id: str

    async def call_api(self, api: str, **data: Any) -> Any: ...


MessageLike = Message | MessageSegment | str | UniMessage[Any]


def export_msg(msg: UniMessage[Any]) -> Message:
    return cast(Message, msg.export_sync(adapter="OneBot V11"))


def handle_input_message(msg: MessageLike) -> Message:
    if isinstance(msg, Message):
        return msg

    if isinstance(msg, MessageSegment):
        return Message(msg)

    if isinstance(msg, str):
        return Message(MessageSegment.text(msg))

    return export_msg(msg)
