from typing import Type

from nonebot.adapters.onebot.v11 import Message

from src.db.crud import getUser
from ..basics import CheckEnvironment, CommandBase
from ...config import config
from models import *


async def getSender(env: CheckEnvironment):
    return await getUser(env.session, env.sender)


def isValidColorCode(raw: str):
    if len(raw) != 7 and len(raw) != 4:
        return False
    if raw[0] != "#":
        return False
    for i in raw[1:]:
        if i not in "0123456789abcdefABCDEF":
            return False
    return True


def requireAdmin(cls: Type[CommandBase]):
    class _cls(cls):
        async def check(self, env: CheckEnvironment) -> Message | None:
            if env.group_id not in config.admin_groups:
                return None

            return await super().check(env)

    return _cls
