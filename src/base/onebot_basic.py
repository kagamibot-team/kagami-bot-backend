from typing import Any, Protocol


from nonebot.adapters.onebot.v11 import Message, MessageSegment

from nonebot_plugin_alconna.uniseg.message import UniMessage
from nonebot_plugin_alconna import Reply, Image, Text, At, Emoji


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


MessageLike = Message | MessageSegment | str | UniMessage[Any]


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
        elif isinstance(seg, Reply):
            result.append(MessageSegment.reply(int(seg.id)))
        else:
            raise Exception(
                f"暂时不支持处理 {seg}，请联系 Passthem 添加对这种消息的支持"
            )

    return result


def handle_input_message(msg: MessageLike) -> Message:
    if isinstance(msg, Message):
        return msg
    elif isinstance(msg, MessageSegment):
        return Message(msg)
    elif isinstance(msg, str):
        return Message(MessageSegment.text(msg))
    else:
        return export_msg(msg)
