from dataclasses import dataclass
import re
from sqlalchemy import select
from nonebot.adapters.onebot.v11 import Message

from ...putils.command import CheckEnvironment, at, text, image, Command

from ..models import *
from ..models.data import hangupSkin

from ..cores import handlePick

from ..messages import caughtMessage, help, displayAward, drawStatus, drawStorage


from .keywords import *
from .tools import getSender


class Catch(Command):
    def __init__(self):
        super().__init__(f"^{KEYWORD_BASE_COMMAND} ?(\\d+)?", "$")

    def errorMessage(self, env: CheckEnvironment):
        return None

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        maxCount = 1

        if result.group(2) is not None and result.group(2).isdigit():
            maxCount = int(result.group(2))

        picksResult = await handlePick(env.session, env.sender, maxCount)
        message = await caughtMessage(env.session, picksResult)

        await env.session.commit()
        return message


class CrazyCatch(Command):
    def __init__(self):
        super().__init__(f"^({KEYWORD_CRAZY}{KEYWORD_BASE_COMMAND}|kz)", "$")

    def errorMessage(self, env: CheckEnvironment):
        return None

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        picksResult = await handlePick(env.session, env.sender, -1)
        message = await caughtMessage(env.session, picksResult)

        await env.session.commit()
        return message


class CatchHelp(Command):
    def __init__(self):
        super().__init__(f"^{KEYWORD_BASE_COMMAND}? ?(help|帮助)", "( admin)?")

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        return help(result.group(3) != None)


@dataclass
class CatchStorage(Command):
    commandPattern: str = f"^{KEYWORD_BASE_COMMAND}?{KEYWORD_STORAGE}"
    argsPattern: str = "$"

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        storageImage = await drawStorage(env.session, await getSender(env))

        return Message(
            [
                at(env.sender),
                text(f" 的小哥库存："),
                await image(storageImage),
            ]
        )


class CatchProgress(Command):
    def __init__(self):
        super().__init__(f"^{KEYWORD_BASE_COMMAND}{KEYWORD_PROGRESS}", "$")

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return None

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        img = await drawStatus(env.session, await getSender(env))

        return Message(
            [
                at(env.sender),
                text(f" 的小哥收集进度："),
                await image(img),
            ]
        )


class CatchFilterNoDescription(Command):
    def __init__(self):
        super().__init__(
            f"^:: ?{KEYWORD_EVERY}?缺描述",
            " *$",
        )

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        lacks = (
            await env.session.execute(
                select(Award).filter(
                    Award.description
                    == "这只小哥还没有描述，它只是静静地躺在这里，等待着别人给他下定义。"
                )
            )
        ).scalars()
        lacks = [a.name for a in lacks]

        return Message([at(env.sender), text(" " + ", ".join(lacks))])


@dataclass
class CatchDisplay(Command):
    commandPattern: str = f"^{KEYWORD_DISPLAY} ?{KEYWORD_AWARDS}? "
    argsPattern: str = "(\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return None

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        name = result.group(3)
        award = (
            await env.session.execute(select(Award).filter(Award.name == name))
        ).scalar_one_or_none()

        if award is None:
            return Message([at(env.sender), text(f" 你没有名字叫 {name} 的小哥")])

        ac = (
            await env.session.execute(
                select(AwardCountStorage)
                .filter(AwardCountStorage.target_award == award)
                .filter(AwardCountStorage.target_user == await getSender(env))
            )
        ).scalar_one_or_none()

        if ac is None or ac.award_count <= 0:
            return Message([at(env.sender), text(f" 你没有名字叫 {name} 的小哥")])

        return await displayAward(env.session, award, await getSender(env))


@dataclass
class CatchHangUpSkin(Command):
    commandPattern: str = f"{KEYWORD_CHANGE} ?{KEYWORD_SKIN}"
    argsPattern: str = " (\\S+)( \\S+)?$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [at(env.sender), text(" 格式不对，格式是 设置皮肤 小哥名字 皮肤名字")]
        )

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        award = (
            await env.session.execute(
                select(Award).filter(Award.name == result.group(3))
            )
        ).scalar_one_or_none()

        if award is None:
            return self.notExists(env, result.group(3))

        if result.group(4) is not None:
            skin = (
                await env.session.execute(
                    select(AwardSkin)
                    .filter(AwardSkin.name == result.group(4)[1:])
                    .filter(AwardSkin.applied_award == award)
                )
            ).scalar_one_or_none()

            if skin is None:
                return self.notExists(env, result.group(4)[1:])

            res = await hangupSkin(env.session, await getSender(env), skin)

            if not res:
                return Message([at(env.sender), text(" 你没有这个皮肤哦")])

            await env.session.commit()
            return Message([at(env.sender), text(" 皮肤换好了")])

        await hangupSkin(env.session, await getSender(env), None)
        await env.session.commit()
        return Message([at(env.sender), text(" 皮肤改回默认了")])


@dataclass
class CatchShowUpdate(Command):
    commandPattern: str = f"^{KEYWORD_BASE_COMMAND} ?{KEYWORD_UPDATE}"
    argsPattern: str = "$"

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]) -> Message | None:
        return await super().handleCommand(env, result)


__all__ = [
    "Catch",
    "CrazyCatch",
    "CatchHelp",
    "CatchStorage",
    "CatchProgress",
    "CatchFilterNoDescription",
    "CatchDisplay",
    "CatchHangUpSkin",
]
