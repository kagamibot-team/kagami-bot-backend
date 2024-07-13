from typing import Type

from nonebot.adapters.onebot.v11 import Message

from .old_version import CheckEnvironment, CommandBase
from src.common.config import config


def requireAdmin(cls: Type[CommandBase]):
    class _cls(cls):
        async def check(self, env: CheckEnvironment) -> Message | None:
            if (
                env.group_id not in config.admin_groups
                and env.sender != config.admin_id
            ):
                return None

            return await super().check(env)

    return _cls
