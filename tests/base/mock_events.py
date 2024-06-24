from typing import Any, Iterable
from nonebot_plugin_alconna import Segment
from nonebot_plugin_alconna.uniseg.message import UniMessage
from src.base.onebot_basic import Recallable
from src.imports import *

from nonebot.adapters.onebot.v11 import Message


class MockReceipt(Recallable):
    async def recall(self, *args: Any, **kwargs: Any) -> Any:
        logger.info(f"Recalling message: {args}, {kwargs}")


class MockUniMessageContext(UniMessageContext):
    message: UniMessage[Any]
    sender: int = 0
    sent: list[UniMessage[Any]]

    def __init__(self, message: UniMessage[Any], sender: int = 0) -> None:
        self.message = message
        self.sender = sender
        self.sent = []

    async def getMessage(self) -> UniMessage[Segment]:
        return self.message

    async def send(self, message: Iterable[Any] | str) -> Recallable:
        self.sent.append(UniMessage(message))
        return MockReceipt()

    def getSenderId(self) -> int:
        return self.sender

    async def reply(self, message: Iterable[Any] | str) -> Recallable:
        return await self.send(message)


class MockOnebot:
    self_id: str

    called_apis: list[tuple[str, dict[str, Any]]]
    sent_messages: list[Message]

    def __init__(self, self_id: str) -> None:
        self.self_id = self_id
        self.called_apis = []
        self.sent_messages = []

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


class MockOnebotEvent:
    user_id: int
    to_me: bool
    message: Message

    def __init__(self, user_id: int, to_me: bool, message: Message) -> None:
        self.user_id = user_id
        self.to_me = to_me
        self.message = message

    def get_message(self) -> Message:
        return self.message


class MockOnebotGroupEvent(MockOnebotEvent):
    group_id: int

    def __init__(
        self, user_id: int, to_me: bool, message: Message, group_id: int
    ) -> None:
        super().__init__(user_id, to_me, message)
        self.group_id = group_id
