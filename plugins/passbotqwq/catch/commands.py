from dataclasses import dataclass
import pathlib
import re
import time
from typing import Any, Callable, Coroutine, TypeVar
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from ..putils.download import download, writeData
from .models import Award, Level
from ..putils.draw import _hello_world, imageToBytes
from .messages import (
    allAwards,
    allLevels,
    cannotGetAward,
    displayAward,
    displayWrongFormat,
    getAward,
    help,
    modifyOk,
    noAwardNamed,
    setIntervalWrongFormat,
    settingOk,
    storageCheck,
)
from .data import (
    _dev_migrate_images,
    clearUnavailableAward,
    ensureNoSameAid,
    getAllAwards,
    getAllAwardsOfOneUser,
    getAllLevels,
    getAwardByAwardName,
    getAwardsFromLevelId,
    getImageTarget,
    getLevelByLevelName,
    userData,
    globalData,
)
from .images import drawStorage
from ..putils.text_format_check import isFloat, not_negative, regex, A_SIMPLE_RULE

KEYWORD_BASE_COMMAND = "(抓小哥|zhua|ZHUA)"

KEYWORD_CHANGE = "(更改|改变|修改|修正|修订|变化|调整|设置|更新)"
KEYWORD_EVERY = "(所有|一切|全部)"
KEYWORD_PROGRESS = "(进度|成就|进展)"

KEYWORD_INTERVAL = "(时间|周期|间隔)"
KEYWORD_AWARDS = "(物品|奖品|小哥)"
KEYWORD_LEVEL = "(等级|级别)"


@dataclass
class CheckEnvironment:
    sender: int
    text: str
    message_id: int
    message: Message


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
    @match(regex(f"^{KEYWORD_BASE_COMMAND}$"))
    async def check(self, env: CheckEnvironment):
        tm = time.time()
        delta = userData.get(env.sender).lastCatch + globalData.get().timeDelta - tm

        if delta > 0:
            return cannotGetAward(env.sender, delta)

        award = globalData.get().pick()

        with userData.open(env.sender) as d:
            d.addAward(award.aid)
            d.lastCatch = tm

            countAward = d.awardCounter[award.aid]

        newOne = "【新!】" if countAward == 1 else ""

        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(
                    f"\n{newOne}你刚刚抓到了你的第 {countAward} 只："
                    + award.name
                    + "！"
                ),
                MessageSegment.image(pathlib.Path(award.imgPath)),
                MessageSegment.text(
                    "稀有度：【"
                    + globalData.get().getLevelByLid(award.levelId).name
                    + "】"
                    + f"\n\n{award.description}"
                ),
            ]
        )


class CatchHelp(Command):
    def __init__(self):
        super().__init__(f"^{KEYWORD_BASE_COMMAND}? ?(help|帮助)", "( admin)?")

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return help(result.group(3) != None)


class CatchStorage(CommandBase):
    @match(regex(f"^{KEYWORD_BASE_COMMAND}?(库存|kc)$"))
    async def check(self, env: CheckEnvironment) -> Message | None:
        image, tm = drawStorage(env.sender)
        storageImage = imageToBytes(image)

        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(f" 的小哥库存 (Render time: {round(tm, 2)})："),
                MessageSegment.image(storageImage),
            ]
        )

        # return storageCheck(env.sender)


class CatchAllLevel(CommandBase):
    @match(regex(f"^:: ?{KEYWORD_EVERY}{KEYWORD_LEVEL}$"))
    async def check(self, env: CheckEnvironment) -> Message | None:
        return allLevels()


class CatchAllAwards(CommandBase):
    @match(regex(f"^:: ?{KEYWORD_EVERY}{KEYWORD_AWARDS}$"))
    async def check(self, env: CheckEnvironment) -> Message | None:
        ensureNoSameAid()
        return allAwards()


class ImageTest(CommandBase):
    @match(regex("^/hello$"))
    async def check(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                MessageSegment.reply(env.message_id),
                MessageSegment.image(_hello_world()),
            ]
        )


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
                MessageSegment.text(
                    f" 清空了 {result.group(2)} 背包里的所有 {result.group(4)}"
                ),
            ]
        )


class CatchProgress(Command):
    def __init__(self):
        super().__init__(f"^{KEYWORD_BASE_COMMAND}{KEYWORD_PROGRESS}", "$")

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return None

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        prog: list[str] = []

        awards = getAllAwardsOfOneUser(env.sender)

        for level in getAllLevels():
            if level.name == "名称已丢失":
                continue

            _awards = len([a for a in awards if a.levelId == level.lid])
            _all = len(getAwardsFromLevelId(level.lid))

            prog.append(f"等级【{level.name}】的收集进度 {_awards}/{_all}")

        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text("你的收集进度为：\n\n" + "\n".join(prog)),
            ]
        )


@dataclass
class CatchModifyCallback(CallbackBase):
    modifyType: str
    modifyObject: Award

    def callbackMessage(self, env: CheckEnvironment, reason: str = ""):
        info: str = f" {reason}，请再次输入它的 " if reason else " 请输入它的 "
        info = info + self.modifyType

        return Message([MessageSegment.at(env.sender), MessageSegment.text(info)])

    async def callback(self, env: CheckEnvironment):
        if self.modifyType == "名称":
            if not re.match("^\\S+$", env.text):
                raise WaitForMoreInformationException(
                    self, self.callbackMessage(env, "名称中不能包含空格")
                )

            self.modifyObject.name = env.text

            with globalData as d:
                d.removeAwardsByAid(self.modifyObject.aid)
                d.awards.append(self.modifyObject)

            return modifyOk()

        if self.modifyType == "等级":
            level = getLevelByLevelName(env.text)

            if len(level) == 0:
                raise WaitForMoreInformationException(
                    self, self.callbackMessage(env, "你输入的等级不存在")
                )

            self.modifyObject.levelId = level[0].lid

            with globalData as d:
                d.removeAwardsByName(self.modifyObject.name)
                d.awards.append(self.modifyObject)

            return modifyOk()

        if self.modifyType == "描述":
            self.modifyObject.description = env.text

            with globalData as d:
                d.removeAwardsByName(self.modifyObject.name)
                d.awards.append(self.modifyObject)

            return modifyOk()

        if len(images := env.message.include("image")) != 1:
            raise WaitForMoreInformationException(
                self, self.callbackMessage(env, "你没有发送图片，或者发送了多张图片")
            )

        image = images[0]

        fp = getImageTarget(self.modifyObject)

        await writeData(await download(image.data["url"]), fp)

        self.modifyObject.updateImage(fp)

        with globalData as d:
            d.removeAwardsByName(self.modifyObject.name)
            d.awards.append(self.modifyObject)

        return modifyOk()


class CatchModify(Command):
    def __init__(self):
        super().__init__(
            f"^:: ?{KEYWORD_CHANGE} ?{KEYWORD_AWARDS} ?(名称|图片|等级|描述)",
            " (\\S+)",
        )

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(
                    " 格式错误，允许的格式有：\n"
                    "::更改奖品 名称 <奖品的名字>\n"
                    "::更改奖品 图片 <奖品的名字>\n"
                    "::更改奖品 描述 <奖品的名字>\n"
                    "::更改奖品 等级 <奖品的名字>"
                ),
            ]
        )

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        modifyType = result.group(3)
        modifyObject = result.group(4)

        award = getAwardByAwardName(modifyObject)

        if len(award) == 0:
            return self.notExists(env, modifyObject)

        callback = CatchModifyCallback(modifyType, award[0])

        raise WaitForMoreInformationException(callback, callback.callbackMessage(env))


@dataclass
class CatchLevelModifyCallback(CallbackBase):
    modifyType: str
    modifyObject: Level

    def callbackMessage(self, env: CheckEnvironment, reason: str = ""):
        info: str = f" {reason}，请再次输入它的 " if reason else " 请输入它的 "
        info = info + self.modifyType

        return Message([MessageSegment.at(env.sender), MessageSegment.text(info)])

    async def callback(self, env: CheckEnvironment):
        if self.modifyType == "名称":
            if " " in env.text:
                raise WaitForMoreInformationException(
                    self, self.callbackMessage(env, "名称中不能包含空格")
                )

            oldName = self.modifyObject.name
            self.modifyObject.name = env.text

            with globalData as d:
                d.removeLevelByName(oldName)
                d.levels.append(self.modifyObject)

            return modifyOk()

        if not not_negative()(env.text):
            raise WaitForMoreInformationException(
                self, self.callbackMessage(env, "请输入一个不小于零的数")
            )

        self.modifyObject.weight = float(env.text)

        with globalData as d:
            d.removeLevelByName(self.modifyObject.name)
            d.levels.append(self.modifyObject)

        return modifyOk()


class CatchLevelModify(Command):
    def __init__(self):
        super().__init__(
            f"^:: ?{KEYWORD_CHANGE} ?{KEYWORD_LEVEL} ?(名称|权重)",
            " (\\S+)",
        )

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(
                    " 格式错误，允许的格式有：\n"
                    "::更改等级 名称 <等级的名字>\n"
                    "::更改等级 权重 <等级的名字>"
                ),
            ]
        )

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        modifyType = result.group(3)
        modifyObject = result.group(4)

        level = getLevelByLevelName(modifyObject)

        if len(level) == 0:
            return self.notExists(env, modifyObject)

        callback = CatchLevelModifyCallback(modifyType, level[0])

        raise WaitForMoreInformationException(callback, callback.callbackMessage(env))


class CatchFilterNoDescription(Command):
    def __init__(self):
        super().__init__(
            f"^:: ?{KEYWORD_EVERY}?缺描述",
            " *$",
        )

    def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        lacks = getAllAwards()
        lacks = [
            a.name
            for a in lacks
            if a.description
            == "这只小哥还没有描述，它只是静静地躺在这里，等待着别人给他下定义。"
        ]

        return Message(
            [MessageSegment.at(env.sender), MessageSegment.text(" " + ", ".join(lacks))]
        )


enabledCommand: list[CommandBase] = [
    Catch(),
    CatchHelp(),
    CatchStorage(),
    CatchAllAwards(),
    CatchAllLevel(),
    CatchSetInterval(),
    CatchModify(),
    CatchLevelModify(),
    CatchProgress(),
    CatchFilterNoDescription(),
]
