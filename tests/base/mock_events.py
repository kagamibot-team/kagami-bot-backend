from typing import Any, Iterable
from nonebot_plugin_alconna import Segment
from nonebot_plugin_alconna.uniseg.message import UniMessage
from src.base.command_events import Recallable
from src.imports import *

from nonebot.adapters.onebot.v11 import Message


class MockReceipt(Recallable):
    async def recall(self, *args: Any, **kwargs: Any) -> Any:
        logger.info(f"Recalling message: {args}, {kwargs}")


@dataclass
class MockUniMessageContext(UniMessageContext):
    message: UniMessage[Any]
    sender: int = 0

    sent: list[UniMessage[Any]] = field(default_factory=list)

    async def getMessage(self) -> UniMessage[Segment]:
        return self.message

    async def send(self, message: Iterable[Any] | str) -> Recallable:
        self.sent.append(UniMessage(message))
        return MockReceipt()

    def getSenderId(self) -> int:
        return self.sender

    async def reply(self, message: Iterable[Any] | str) -> Recallable:
        return await self.send(message)


@dataclass
class MockOnebot:
    self_id: str

    called_apis: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    sent_messages: list[Message] = field(default_factory=list)

    async def call_api(self, api: str, **data: Any) -> Any:
        self.called_apis.append((api, data))

        if api == "send_private_msg" or api == "send_group_msg":
            assert "message" in data.keys()
            self.sent_messages.append(data["message"])
            return {"message_id": 0}

        if api == "get_group_member_info":
            return {
                "card": "这是我的群名片",
                "nickname": "这是我的昵称",
                "role": "admin",
            }
        
        if api == "get_stranger_info":
            return {
                "nick": "这是我的昵称",
            }


@dataclass
class MockOnebotEvent:
    user_id: int
    to_me: bool
    message: Message

    def get_message(self) -> Message:
        return self.message


@dataclass
class MockOnebotGroupEvent(MockOnebotEvent):
    group_id: int
