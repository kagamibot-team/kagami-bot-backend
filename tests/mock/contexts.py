import random
from typing import Any

import faker
from nonebot import get_driver, logger
from src.common.classes.command_events import GroupContext

from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot, Adapter
from nonebot.adapters.onebot.v11.event import Sender

fake = faker.Faker("zh_CN")


class MockOnebotBot(Bot):
    async def call_api(self, api: str, **data) -> Any:
        logger.info(f"API {api} was called with {data}")


_a = Adapter(get_driver())


class MockGroupContext(GroupContext):
    def __init__(self, message: Message):
        sender = random.randint(1, 5000000000)
        selfId = random.randint(1, 5000000000)

        super().__init__(GroupMessageEvent(
            time=0,
            self_id=selfId,
            post_type="message",
            sub_type="",
            user_id=sender,
            message_type="group",
            message_id=random.randint(1, 5000000000),
            message=message,
            original_message=message,
            raw_message="",
            font=0,
            sender=Sender(user_id=sender, nickname=fake.name()),
            group_id=random.randint(1, 5000000000),
        ), MockOnebotBot(_a, str(selfId)))
