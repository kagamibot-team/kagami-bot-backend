import pathlib
import re
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot
from plugins.passbotqwq.putils.draw.typing import PILImage
from ..putils.draw import imageToBytes
from dataclasses import dataclass
from nonebot_plugin_orm import async_scoped_session


def at(sender: int):
    return MessageSegment.at(sender)


def text(text: str):
    return MessageSegment.text(text)


async def image(image: PILImage):
    return MessageSegment.image(imageToBytes(image))


async def localImage(image: str):
    return MessageSegment.image(pathlib.Path(image))


@dataclass
class CheckEnvironment:
    sender: int
    text: str
    message_id: int
    message: Message
    session: async_scoped_session
    bot: Bot
    group_id: int


class CommandBase:
    async def check(self, env: CheckEnvironment) -> Message | None:
        return None


class CallbackBase(CommandBase):
    async def check(self, env: CheckEnvironment) -> Message | None:
        if env.text.lower() == "::cancel":
            return Message(
                [MessageSegment.at(env.sender), MessageSegment.text(" 已取消")]
            )

        return await self.callback(env)

    async def callback(self, env: CheckEnvironment) -> Message | None:
        return None


class WaitForMoreInformationException(Exception):
    def __init__(self, callback: CallbackBase, message: Message | None) -> None:
        self.callback = callback
        self.message = message


@dataclass
class Command(CommandBase):
    commandPattern: str
    argsPattern: str

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
        if len(env.message.exclude("text")) > 0:
            return None

        if not re.match(self.commandPattern, env.text):
            return None

        matchRes = re.match(self.commandPattern + self.argsPattern, env.text)

        if not matchRes:
            return self.errorMessage(env)

        return await self.handleCommand(env, matchRes)
