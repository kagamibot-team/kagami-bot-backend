from dataclasses import dataclass
import re
from typing import Any, Callable, Coroutine, TypeVar
from sqlalchemy import delete, select
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot

from plugins.passbotqwq.catch.messages.texts import displayAward
from plugins.passbotqwq.putils.draw.typing import PILImage

from .models.crud import getOrCreateUser
from .models.data import addAward, setEveryoneInterval

from .cores import handlePick

from ..putils.download import download, writeData
from ..putils.draw import imageToBytes
from .messages import (
    allAwards,
    allLevels,
    caughtMessage,
    help,
    modifyOk,
    setIntervalWrongFormat,
    settingOk,
)

from .models import *

from .messages.images import drawStatus, drawStorage, getImageTarget
from ..putils.text_format_check import not_negative, A_SIMPLE_RULE

from nonebot_plugin_orm import async_scoped_session

KEYWORD_BASE_COMMAND = "(抓小哥|zhua|ZHUA)"

KEYWORD_CHANGE = "(更改|改变|修改|修正|修订|变化|调整|设置|更新)"
KEYWORD_EVERY = "(所有|一切|全部)"
KEYWORD_PROGRESS = "(进度|成就|进展|jd)"

KEYWORD_INTERVAL = "(时间|周期|间隔)"
KEYWORD_AWARDS = "(物品|小哥)"
KEYWORD_LEVEL = "(等级|级别)"

KEYWORD_CRAZY = "(连|l|狂|k)"
KEYWORD_DISPLAY = "(展示|display|查看)"
KEYWORD_STORAGE = "(库存|kc)"

KEYWORD_REMOVE = "(删除|删掉)"
KEYWORD_CREATE = "(创建|新建|添加)"


def at(sender: int):
    return MessageSegment.at(sender)


def text(text: str):
    return MessageSegment.text(text)


async def image(image: PILImage):
    return MessageSegment.image(imageToBytes(image))


@dataclass
class CheckEnvironment:
    sender: int
    text: str
    message_id: int
    message: Message
    session: async_scoped_session
    bot: Bot

    async def getSender(self):
        return await getOrCreateUser(self.session, self.sender)


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


class Catch(Command):
    def __init__(self):
        super().__init__(f"^{KEYWORD_BASE_COMMAND} ?(\\d+)?", "$")

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return None

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        maxCount = 1

        if result.group(2) is not None and result.group(2).isdigit():
            maxCount = int(result.group(2))

        picksResult = await handlePick(env.session, env.sender, maxCount)
        message = await caughtMessage(picksResult)

        await env.session.commit()
        return message


class CrazyCatch(Command):
    def __init__(self):
        super().__init__(f"^({KEYWORD_CRAZY}{KEYWORD_BASE_COMMAND}|kz)", "$")

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return None

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        picksResult = await handlePick(env.session, env.sender, -1)
        message = await caughtMessage(picksResult)

        await env.session.commit()
        return message


class CatchHelp(Command):
    def __init__(self):
        super().__init__(f"^{KEYWORD_BASE_COMMAND}? ?(help|帮助)", "( admin)?")

    def syncHandleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return help(result.group(3) != None)


@dataclass
class CatchStorage(Command):
    commandPattern: str = f"^{KEYWORD_BASE_COMMAND}?{KEYWORD_STORAGE}"
    argsPattern: str = "$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        image, tm = await drawStorage(await env.getSender())
        storageImage = imageToBytes(image)

        return Message(
            [
                at(env.sender),
                text(f" 的小哥库存 (Render time: {round(tm, 2)})："),
                MessageSegment.image(storageImage),
            ]
        )


@dataclass
class CatchAllLevel(Command):
    commandPattern: str = f"^:: ?{KEYWORD_EVERY}{KEYWORD_LEVEL}"
    argsPattern: str = "$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return await allLevels(env.session)


@dataclass
class CatchAllAwards(Command):
    commandPattern: str = f"^:: ?{KEYWORD_EVERY}{KEYWORD_AWARDS}"
    argsPattern: str = "$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return await allAwards(env.session)


class CatchSetInterval(Command):
    def __init__(self):
        super().__init__(f"^:: ?{KEYWORD_CHANGE} ?{KEYWORD_INTERVAL}", " ?(-?[0-9]+)$")

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return setIntervalWrongFormat()

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        interval = int(result.group(3))
        await setEveryoneInterval(env.session, interval)
        message = settingOk()

        await env.session.commit()
        return message


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

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        award = (
            await env.session.execute(
                select(Award).filter(Award.name == result.group(2))
            )
        ).scalar_one_or_none()

        if award is None:
            return self.notExists(env, result.group(2))

        await addAward(env.session, await getOrCreateUser(env.session, int(result.group(1))), award, 1)

        message = Message(
            [at(env.sender), text(f" : 已将 {award.name} 给予用户 "), at(env.sender)]
        )

        await env.session.commit()

        return message


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

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        if result.group(2) == None:
            await env.session.execute(
                delete(AwardCountStorage).where(
                    AwardCountStorage.target_user == await env.getSender()
                )
            )

            await env.session.commit()

            return Message(
                [MessageSegment.at(env.sender), MessageSegment.text(f" 清空了你的背包")]
            )

        user = (
            await env.session.execute(
                select(UserData).filter(UserData.qq_id == int(result.group(2)))
            )
        ).scalar_one_or_none()

        if user is None:
            return self.notExists(env, result.group(2))

        if result.group(4) == None:
            await env.session.execute(
                delete(AwardCountStorage).where(AwardCountStorage.target_user == user)
            )

            await env.session.commit()

            return Message(
                [
                    MessageSegment.at(env.sender),
                    MessageSegment.text(f" 清空了 {result.group(2)} 的背包"),
                ]
            )

        await env.session.execute(
            delete(AwardCountStorage)
            .where(AwardCountStorage.target_user == user)
            .where(AwardCountStorage.target_award.has(Award.name == result.group(4)))
        )

        await env.session.commit()

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

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:

        image, tm = await drawStatus(env.session, await env.getSender())

        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(f" 的小哥收集进度 (Render time: {round(tm, 2)})："),
                MessageSegment.image(imageToBytes(image)),
            ]
        )


@dataclass
class CatchRemoveAward(Command):
    commandPattern: str = f"^:: ?{KEYWORD_REMOVE} ?{KEYWORD_AWARDS}"
    argsPattern: str = " ?(\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(text("你的格式有问题，应该是 ::删除小哥 小哥的名字"))

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        await env.session.execute(delete(Award).where(Award.name == result.group(3)))
        await env.session.commit()
        return Message(text("已经删除了"))


@dataclass
class CatchModifyCallback(CallbackBase):
    modifyType: str
    modifyObject: Callable[[async_scoped_session], Coroutine[Any, Any, Award | None]]


    def callbackMessage(self, env: CheckEnvironment, reason: str = ""):
        info: str = f" {reason}，请再次输入它的 " if reason else " 请输入它的 "
        info = info + self.modifyType

        return Message([MessageSegment.at(env.sender), MessageSegment.text(info)])


    async def callback(self, env: CheckEnvironment):
        modifyObject = await self.modifyObject(env.session)
        assert modifyObject is not None

        if self.modifyType == "名称":
            if not re.match("^\\S+$", env.text):
                raise WaitForMoreInformationException(
                    self, self.callbackMessage(env, "名称中不能包含空格")
                )

            modifyObject.name = env.text

            await env.session.commit()
            return modifyOk()

        if self.modifyType == "等级":
            level = (await env.session.execute(select(Level).filter(Level.name == env.text))).scalar_one_or_none()

            if level is None:
                raise WaitForMoreInformationException(
                    self, self.callbackMessage(env, "你输入的等级不存在")
                )

            modifyObject.level_id = level.data_id
            await env.session.commit()
            return modifyOk()

        if self.modifyType == "描述":
            modifyObject.description = env.text
            await env.session.commit()
            return modifyOk()

        if len(images := env.message.include("image")) != 1:
            raise WaitForMoreInformationException(
                self, self.callbackMessage(env, "你没有发送图片，或者发送了多张图片")
            )

        image = images[0]

        fp = getImageTarget(modifyObject)
        await writeData(await download(image.data["url"]), fp)
        modifyObject.img_path = fp
        await env.session.commit()
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
                    "::更改小哥 名称 <小哥的名字>\n"
                    "::更改小哥 图片 <小哥的名字>\n"
                    "::更改小哥 描述 <小哥的名字>\n"
                    "::更改小哥 等级 <小哥的名字>"
                ),
            ]
        )

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        modifyType = result.group(3)
        modifyObject = result.group(4)

        award = (
            await env.session.execute(select(Award).filter(Award.name == modifyObject))
        ).scalar_one_or_none()

        if award is None:
            return self.notExists(env, modifyObject)

        callback = CatchModifyCallback(modifyType, lambda s: s.get(Award, award.data_id))
        raise WaitForMoreInformationException(callback, callback.callbackMessage(env))


@dataclass
class CatchLevelModifyCallback(CallbackBase):
    modifyType: str
    modifyObject: Callable[[async_scoped_session], Coroutine[Any, Any, Level | None]]

    def callbackMessage(self, env: CheckEnvironment, reason: str = ""):
        info: str = f" {reason}，请再次输入它的 " if reason else " 请输入它的 "
        info = info + self.modifyType

        return Message([MessageSegment.at(env.sender), MessageSegment.text(info)])

    async def callback(self, env: CheckEnvironment):
        modifyObject = await self.modifyObject(env.session)
        assert modifyObject is not None

        if self.modifyType == "名称":
            if " " in env.text:
                raise WaitForMoreInformationException(
                    self, self.callbackMessage(env, "名称中不能包含空格")
                )

            modifyObject.name = env.text
            await env.session.commit()
            return modifyOk()

        if not not_negative()(env.text):
            raise WaitForMoreInformationException(
                self, self.callbackMessage(env, "请输入一个不小于零的数")
            )

        modifyObject.weight = float(env.text)
        await env.session.commit()
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

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]) -> Message | None:
        modifyType = result.group(3)
        modifyObject = result.group(4)

        level = (await env.session.execute(select(Level).filter(Level.name == modifyObject))).scalar_one_or_none()

        if level is None:
            return self.notExists(env, modifyObject)

        callback = CatchLevelModifyCallback(modifyType, lambda s: s.get(Level, level.data_id))
        raise WaitForMoreInformationException(callback, callback.callbackMessage(env))


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

        return Message(
            [MessageSegment.at(env.sender), MessageSegment.text(" " + ", ".join(lacks))]
        )


@dataclass
class CatchDisplay(Command):
    commandPattern: str = f"^{KEYWORD_DISPLAY} ?{KEYWORD_AWARDS}?"
    argsPattern: str = " ?(\\S+)( admin)?$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                MessageSegment.at(env.sender),
                MessageSegment.text(" 你的格式有问题，应该是 展示小哥 小哥名字"),
            ]
        )

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        name = result.group(3)
        award = (
            await env.session.execute(select(Award).filter(Award.name == name))
        ).scalar_one_or_none()

        if award is None:
            return Message([at(env.sender), text(f" 你没有名字叫 {name} 的小哥")])

        if not result.group(4):
            ac = (await env.session.execute(select(AwardCountStorage).filter(
                AwardCountStorage.target_award == award
            ).filter(
                AwardCountStorage.target_user == await env.getSender()
            ))).scalar_one_or_none()

            if ac is None or ac.award_count <= 0:
                return Message([
                    at(env.sender),
                    text(f' 你没有名字叫 {name} 的小哥')
                ])

        return displayAward(award)


@dataclass
class CatchCreateAward(Command):
    commandPattern: str = f"^:: ?{KEYWORD_CREATE} ?{KEYWORD_AWARDS}"
    argsPattern: str = " (\\S+) (\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([
            at(env.sender),
            text(' 格式 ::创建小哥 名字 等级')
        ])
    
    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]) -> Message | None:
        _sameName = (await env.session.execute(select(Award).filter(Award.name == result.group(3)))).scalar_one_or_none()
        
        if _sameName is not None:
            return Message([
                at(env.sender),
                text(' 存在重名小哥，请检查一下吧')
            ])
        
        level = (await env.session.execute(select(Level).filter(Level.name == result.group(4)))).scalar_one_or_none()

        if level is None:
            return Message([
                at(env.sender),
                text(' 等级名字不存在')
            ])
        
        award = Award(
            name=result.group(3),
            level=level
        )

        env.session.add(award)
        await env.session.commit()

        return Message([
            at(env.sender),
            text(' 添加成功！')
        ])


enabledCommand: list[CommandBase] = [
    Catch(),
    CrazyCatch(),
    CatchHelp(),
    CatchStorage(),
    CatchAllAwards(),
    CatchAllLevel(),
    CatchSetInterval(),
    CatchModify(),
    CatchLevelModify(),
    CatchProgress(),
    CatchFilterNoDescription(),
    CatchRemoveAward(),
    CatchDisplay(),
    CatchCreateAward(),
    Give(),
    Clear(),
]
