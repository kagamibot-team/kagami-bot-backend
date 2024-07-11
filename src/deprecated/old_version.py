import re
from dataclasses import dataclass
from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession
from src.common.config import config

from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment


def at(sender: int):
    return MessageSegment.at(sender)


def text(text: str):
    return MessageSegment.text(text)

def databaseIO():
    def _decorator(cls: Type[Command]):
        class _Command(cls):
            async def handleCommand(
                self, env: "CheckEnvironment", result: re.Match[str]
            ) -> Message | None:
                msg = await super().handleCommand(env, result)
                await env.session.commit()
                return msg

        return _Command

    return _decorator


@dataclass
class CheckEnvironment:
    sender: int
    text: str
    message_id: int
    message: Message
    session: AsyncSession
    bot: Bot
    group_id: int


class CommandBase:
    async def check(self, env: CheckEnvironment) -> Message | None:
        return None


@dataclass
class Command(CommandBase):
    commandPattern: str = "^$"
    argsPattern: str = "$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return None

    def notExists(self, env: CheckEnvironment, item: str):
        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(f" 你输入的 {item} 不存在"),
            ]
        )

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return None

    async def check(self, env: CheckEnvironment) -> Message | None:
        if config.enable_white_list and env.group_id not in config.white_list_groups:
            return

        if len(env.message.exclude("text")) > 0:
            return None

        if not re.match(self.commandPattern, env.text):
            return None

        matchRes = re.match(self.commandPattern + self.argsPattern, env.text)

        if not matchRes:
            return self.errorMessage(env)

        return await self.handleCommand(env, matchRes)


__all__ = [
    "at",
    "text",
    "CheckEnvironment",
    "CommandBase",
    "Command",
    "databaseIO",
]
