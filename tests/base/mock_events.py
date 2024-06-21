from typing import Any, Iterable
from nonebot_plugin_alconna import Segment
from nonebot_plugin_alconna.uniseg.message import UniMessage
from src.base.command_events import Recallable
from src.imports import *


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
