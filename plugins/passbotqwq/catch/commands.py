from dataclasses import dataclass
import re
import time
from typing import Any, Callable, Coroutine, TypeVar, TypedDict

from .messages import (
    allAwards,
    allLevels,
    cannotGetAward,
    displayAward,
    displayWrongFormat,
    getAward,
    help,
    noAwardNamed,
    setIntervalWrongFormat,
    settingOk,
    storageCheck,
)
from .data import clearUnavailableAward, getAwardByAwardName, getLevelByLevelName, userData, globalData
from ..putils.text_format_check import isFloat, regex, A_SIMPLE_RULE
from nonebot.adapters.onebot.v11 import Message, MessageSegment


KEYWORD_CHANGE = "(更改|改变|修改|修正|修订|变化|调整|设置|更新)"
KEYWORD_EVERY = "(所有|一切|全部)"

KEYWORD_INTERVAL = "(时间|周期|间隔)"
KEYWORD_AWARDS = "(物品|奖品|小哥)"
KEYWORD_LEVEL = "(等级|级别)"


@dataclass
class CheckEnvironment:
    sender: int
    text: str


class CommandBase:
    async def check(self, env: CheckEnvironment) -> Message | None:
        return None


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

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return None

    async def check(self, env: CheckEnvironment) -> Message | None:
        if not re.match(self.commandPattern, env.text):
            return None

        matchRes = re.match(self.commandPattern + self.argsPattern, env.text)

        if not matchRes:
            return self.errorMessage(env)

        return self.handleCommand(env, matchRes)


CommandBaseSelf = TypeVar("CommandBaseSelf", bound="CommandBase")


def match(rule: A_SIMPLE_RULE):
    def _decorator(
        func: Callable[
            [CommandBaseSelf, CheckEnvironment], Coroutine[Any, Any, Message | None]
        ]
    ):
        async def clsFunc(self: CommandBaseSelf, env: CheckEnvironment):
            if not rule(env.text):
                return

            return await func(self, env)

        return clsFunc

    return _decorator


class Catch(CommandBase):
    @match(regex("^(抓抓|zz)$"))
    async def check(self, env: CheckEnvironment):
        tm = time.time()
        delta = userData.get(env.sender).lastCatch + globalData.get().timeDelta - tm

        if delta > 0:
            return cannotGetAward(env.sender, delta)

        award = globalData.get().pick()

        with userData.open(env.sender) as d:
            d.addAward(award.aid)
            d.lastCatch = tm

        return getAward(env.sender, award)


class CatchHelp(CommandBase):
    @match(regex("^(抓抓|zz) ?(help|帮助)$"))
    async def check(self, env: CheckEnvironment) -> Message | None:
        return help()


class CatchStorage(CommandBase):
    @match(regex("^(抓抓|zz)?(库存|kc)$"))
    async def check(self, env: CheckEnvironment) -> Message | None:
        return storageCheck(env.sender)


class CatchAllLevel(CommandBase):
    @match(regex(f"^:: ?{KEYWORD_EVERY}{KEYWORD_LEVEL}$"))
    async def check(self, env: CheckEnvironment) -> Message | None:
        return allLevels()


class CatchAllAwards(CommandBase):
    @match(regex(f"^:: ?{KEYWORD_EVERY}{KEYWORD_AWARDS}$"))
    async def check(self, env: CheckEnvironment) -> Message | None:
        return allAwards()


class CatchSetInterval(Command):
    def __init__(self):
        super().__init__(f"^:: ?{KEYWORD_CHANGE} ?{KEYWORD_INTERVAL}", " ?(-?[0-9]+)$")

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return setIntervalWrongFormat()

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        if not result.group(3).isdigit():
            return self.errorMessage(env)

        interval = int(result.group(3))

        with globalData as d:
            d.timeDelta = interval

        return settingOk()


class CatchChangeLevel(Command):
    def __init__(self):
        super().__init__(
            f"^:: ?{KEYWORD_CHANGE}{KEYWORD_AWARDS} ?{KEYWORD_LEVEL}",
            " (\\S+) (\\S+)$",
        )

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(
                    " 格式错了，应该是 ::改变奖品 等级 <奖品的名字> <等级的名字>"
                ),
            ]
        )

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        awardName = result.group(4)
        levelName = result.group(5)

        awards = getAwardByAwardName(awardName)
        levels = getLevelByLevelName(levelName)

        if len(awards) == 0:
            return self.notExists(env, "奖品 " + awardName)

        if len(levels) == 0:
            return self.notExists(env, "等级 " + levelName)

        with globalData as d:
            d.getAwardByAidStrong(awards[0].aid).levelId = levels[0].lid

        return Message(
            [MessageSegment.at(env.sender), MessageSegment.text(f" 更改好了")]
        )


class Give(Command):
    def __init__(self):
        super().__init__(
            "^/give",
            " (\\d+) (\\S+)$",
        )

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(
                    " Invalid format, expected /give <uid> <awardName>"
                ),
            ]
        )

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        awards = getAwardByAwardName(result.group(2))

        if len(awards) == 0:
            return self.notExists(env, result.group(2))

        with userData.open(int(result.group(1))) as d:
            d.addAward(awards[0].aid)

        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(
                    f" : 已将 {awards[0].name} 给予用户 {result.group(1)}"
                ),
            ]
        )


class Clear(Command):
    def __init__(self):
        super().__init__(
            "^/clear",
            "( (\\d+)( (\\S+))?)?$",
        )

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(" Invalid format."),
            ]
        )

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        if result.group(2) == None:
            with userData.open(env.sender) as d:
                d.awardCounter = {}

            return Message(
                [MessageSegment.at(env.sender), MessageSegment.text(f" 清空了你的背包")]
            )

        if result.group(4) == None:
            with userData.open(int(result.group(2))) as d:
                d.awardCounter = {}

            return Message(
                [
                    MessageSegment.at(env.sender),
                    MessageSegment.text(f" 清空了 {result.group(2)} 的背包"),
                ]
            )
        
        clearUnavailableAward()

        awards = getAwardByAwardName(result.group(4))

        awardIDs = [a.aid for a in awards]

        with userData.open(int(result.group(2))) as d:
            d.awardCounter = {
                key: d.awardCounter[key]
                for key in d.awardCounter.keys()
                if key not in awardIDs
            }

        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(f" 清空了 {result.group(2)} 背包里的所有 {result.group(4)}"),
            ]
        )


enabledCommand: list[CommandBase] = [
    Catch(),
    CatchHelp(),
    CatchStorage(),
    CatchAllAwards(),
    CatchAllLevel(),
    CatchSetInterval(),
    CatchChangeLevel(),
    Give(),
    Clear(),
]
