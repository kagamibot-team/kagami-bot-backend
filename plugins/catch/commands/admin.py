from dataclasses import dataclass
import re
from typing import Any, Callable, Coroutine
from sqlalchemy import delete, select
from nonebot_plugin_orm import async_scoped_session
from nonebot.adapters.onebot.v11 import Message

from ..messages.texts import helpAdmin

from ..putils.command import (
    CheckEnvironment,
    at,
    localImage,
    text,
    Command,
    CallbackBase,
    WaitForMoreInformationException,
)
from ..putils.download import download, writeData
from ..putils.text_format_check import isFloat, not_negative

from ..models import *

from ..messages import (
    allAwards,
    allLevels,
    modifyOk,
    setIntervalWrongFormat,
    settingOk,
    getImageTarget,
    getSkinTarget,
)


from .keywords import *
from .tools import getSender, isValidColorCode, requireAdmin


@requireAdmin
@dataclass
class CatchAllLevel(Command):
    commandPattern: str = f"^:: ?{KEYWORD_EVERY}{KEYWORD_LEVEL}"
    argsPattern: str = "$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return await allLevels(env.session)


@requireAdmin
@dataclass
class CatchAllAwards(Command):
    commandPattern: str = f"^:: ?{KEYWORD_EVERY}{KEYWORD_AWARDS}"
    argsPattern: str = "$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return await allAwards(env.session)


@requireAdmin
class CatchSetInterval(Command):
    def __init__(self):
        super().__init__(f"^:: ?{KEYWORD_CHANGE} ?{KEYWORD_INTERVAL}", " ?(-?[0-9]+)$")

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return setIntervalWrongFormat()

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        interval = int(result.group(3))
        await setInterval(env.session, interval)
        message = settingOk()

        await env.session.commit()
        return message


@requireAdmin
class Give(Command):
    def __init__(self):
        super().__init__(
            "^/give",
            " (\\d+) (\\S+)( \\d+)?$",
        )

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                at(env.sender),
                text(" Invalid format, expected /give <uid> <awardName>"),
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

        count = 1

        if result.group(3):
            count = int(result.group(3)[1:])

        await giveAward(
            env.session,
            await getUser(env.session, int(result.group(1))),
            award,
            count,
        )

        message = Message(
            [at(env.sender), text(f" : 已将 {award.name} 给予用户 {result.group(1)}")]
        )

        await env.session.commit()

        return message


@requireAdmin
class Clear(Command):
    def __init__(self):
        super().__init__(
            "^/clear",
            "( (\\d+)( (\\S+))?)?$",
        )

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                at(env.sender),
                text(" Invalid format."),
            ]
        )

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        if result.group(2) == None:
            await env.session.execute(
                delete(StorageStats).where(StorageStats.user == await getSender(env))
            )

            await env.session.commit()

            return Message([at(env.sender), text(f" 清空了你的背包")])

        user = (
            await env.session.execute(
                select(User).filter(User.qq_id == int(result.group(2)))
            )
        ).scalar_one_or_none()

        if user is None:
            return self.notExists(env, result.group(2))

        if result.group(4) == None:
            await env.session.execute(
                delete(StorageStats).where(StorageStats.user == user)
            )

            await env.session.commit()

            return Message(
                [
                    at(env.sender),
                    text(f" 清空了 {result.group(2)} 的背包"),
                ]
            )

        await env.session.execute(
            delete(StorageStats)
            .where(StorageStats.user == user)
            .where(StorageStats.award.has(Award.name == result.group(4)))
        )

        await env.session.commit()

        return Message(
            [
                at(env.sender),
                text(f" 清空了 {result.group(2)} 背包里的所有 {result.group(4)}"),
            ]
        )


@requireAdmin
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

        return Message([at(env.sender), text(info)])

    async def callback(self, env: CheckEnvironment):
        modifyObject = await self.modifyObject(env.session)
        assert modifyObject is not None

        if self.modifyType == "名称" or self.modifyType == "名字":
            if not re.match("^\\S+$", env.text):
                raise WaitForMoreInformationException(
                    self, self.callbackMessage(env, "名称中不能包含空格")
                )

            modifyObject.name = env.text

            await env.session.commit()
            return modifyOk()

        if self.modifyType == "等级":
            level = (
                await env.session.execute(select(Level).filter(Level.name == env.text))
            ).scalar_one_or_none()

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


@requireAdmin
class CatchModify(Command):
    def __init__(self):
        super().__init__(
            f"^:: ?{KEYWORD_CHANGE} ?{KEYWORD_AWARDS} ?(名字|名称|图片|等级|描述)",
            " (\\S+)",
        )

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                at(env.sender),
                text(
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

        callback = CatchModifyCallback(
            modifyType, lambda s: s.get(Award, award.data_id)
        )
        raise WaitForMoreInformationException(callback, callback.callbackMessage(env))


@requireAdmin
@dataclass
class CatchLevelModify(Command):
    commandPattern: str = (
        f"^:: ?{KEYWORD_CHANGE} ?{KEYWORD_LEVEL} ?(名称|名字|权重|色值|色号|颜色|奖励|金钱|获得|优先级|优先度|优先)"
    )
    argsPattern: str = " ?(\\S+) (.+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_MODIFY_LEVEL_WRONG_FORMAT")])

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        level = (
            await env.session.execute(
                select(Level).filter(Level.name == result.group(4))
            )
        ).scalar_one_or_none()

        if level is None:
            return self.notExists(env, result.group(4))

        modifyElement = result.group(3)
        data = result.group(5)

        if modifyElement == "名称" or modifyElement == "名称":
            level.name = data
        elif modifyElement == "权重":
            if not not_negative()(data):
                return Message([at(env.sender), text("MSG_WEIGHT_INVALID")])

            level.weight = float(data)
        elif (
            modifyElement == "金钱"
            or modifyElement == "获得"
            or modifyElement == "奖励"
        ):
            if not not_negative()(data):
                return Message([at(env.sender), text("MSG_MONEY_INVALID")])

            level.price = int(data)
        elif (
            modifyElement == "优先级"
            or modifyElement == "优先度"
            or modifyElement == "优先"
        ):
            if re.match("^-?\\d+$", data):
                level.sorting_priority = int(data)
        else:
            if not isValidColorCode(data):
                return Message([at(env.sender), text("MSG_COLOR_CODE_INVALID")])

            level.color_code = data

        await env.session.commit()

        return modifyOk()


@requireAdmin
@dataclass
class CatchCreateAward(Command):
    commandPattern: str = f"^:: ?{KEYWORD_CREATE} ?{KEYWORD_AWARDS}"
    argsPattern: str = " (\\S+) (\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text(" 格式 ::创建小哥 名字 等级")])

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        _sameName = (
            await env.session.execute(
                select(Award).filter(Award.name == result.group(3))
            )
        ).scalar_one_or_none()

        if _sameName is not None:
            return Message([at(env.sender), text(" 存在重名小哥，请检查一下吧")])

        level = (
            await env.session.execute(
                select(Level).filter(Level.name == result.group(4))
            )
        ).scalar_one_or_none()

        if level is None:
            return Message([at(env.sender), text(" 等级名字不存在")])

        award = Award(name=result.group(3), level=level)

        env.session.add(award)
        await env.session.commit()

        return Message([at(env.sender), text(" 添加成功！")])


@requireAdmin
@dataclass
class CatchCreateLevel(Command):
    commandPattern: str = f"^:: ?{KEYWORD_CREATE} ?{KEYWORD_LEVEL}"
    argsPattern: str = " (\\S+)$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        levelName = result.group(3)

        existLevel = (
            await env.session.execute(select(Level).filter(Level.name == levelName))
        ).scalar_one_or_none()

        if existLevel is not None:
            return Message([at(env.sender), text("MSG_LEVEL_ALREADY_EXISTS")])

        level = Level(name=levelName, weight=0)

        env.session.add(level)
        await env.session.commit()

        return Message([at(env.sender), text("ok")])


@requireAdmin
@dataclass
class CatchAddSkin(Command):
    commandPattern: str = f"^:: ?{KEYWORD_CREATE} ?{KEYWORD_SKIN}"
    argsPattern: str = " (\\S+) (\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_CREATE_SKIN_WRONG_FORMAT")])

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

        skin = (
            await env.session.execute(select(Skin).filter(Skin.name == result.group(4)))
        ).scalar_one_or_none()

        if skin is not None:
            return Message([at(env.sender), text("MSG_SKIN_ALREADY_EXISTS")])

        skin = Skin(name=result.group(4), award=award)

        env.session.add(skin)
        await env.session.commit()

        return Message([at(env.sender), text("MSG_SKIN_ADDED_SUCCESSFUL")])


@dataclass
class CatchModifySkinCallback(CallbackBase):
    skin_id: int
    param: str

    async def callback(self, env: CheckEnvironment) -> Message | None:
        skin = await env.session.get(Skin, self.skin_id)
        assert skin is not None

        if self.param == "名字" or self.param == "名称":
            if not re.match("^\\S+$", env.text):
                raise WaitForMoreInformationException(
                    self, Message([at(env.sender), text("MSG_INPUT_NAME_WRONG_FORMAT")])
                )

            skin.name = env.text
            await env.session.commit()
            return modifyOk()

        if self.param == "描述":
            skin.extra_description = env.text
            await env.session.commit()
            return modifyOk()

        if self.param == "价钱" or self.param == "价格":
            if not isFloat()(env.text):
                raise WaitForMoreInformationException(
                    self,
                    Message([at(env.sender), text("MSG_INPUT_PRICE_WRONG_FORMAT")]),
                )

            skin.price = float(env.text)
            await env.session.commit()
            return modifyOk()

        if len(images := env.message.include("image")) != 1:
            raise WaitForMoreInformationException(
                self, Message([at(env.sender), text("MSG_IMAGE_WRONG_FORMAT")])
            )

        image = images[0]

        fp = getSkinTarget(skin)
        await writeData(await download(image.data["url"]), fp)
        skin.image = fp
        await env.session.commit()
        return modifyOk()


@requireAdmin
@dataclass
class CatchModifySkin(Command):
    commandPattern: str = (
        f"^:: ?{KEYWORD_CHANGE} ?{KEYWORD_SKIN} ?(名字|名称|描述|图像|图片|价钱|价格)"
    )
    argsPattern: str = " (\\S+) (\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_MODIFY_SKIN_WRONG_FORMAT")])

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        award = (
            await env.session.execute(
                select(Award).filter(Award.name == result.group(4))
            )
        ).scalar_one_or_none()

        if award is None:
            return self.notExists(env, result.group(4))

        skin = (
            await env.session.execute(
                select(Skin)
                .filter(Skin.name == result.group(5))
                .filter(Skin.award == award)
            )
        ).scalar_one_or_none()

        if skin is None:
            return self.notExists(env, result.group(5))

        callback = CatchModifySkinCallback(skin.data_id, result.group(3))  # type: ignore
        raise WaitForMoreInformationException(
            callback, Message([at(env.sender), text("MSG_PLEASE_INPUT")])
        )


@requireAdmin
@dataclass
class CatchAdminDisplay(Command):
    commandPattern: str = f"^:: ?{KEYWORD_DISPLAY}"
    argsPattern: str = " (\\S+)( \\S+)?$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_DISPLAY_ADMIN_WRONG_FORMAT")])

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

        imgUrl = award.img_path
        desc = award.description

        if result.group(3) is not None:
            skin = (
                await env.session.execute(
                    select(Skin)
                    .filter(Skin.name == result.group(3)[1:])
                    .filter(Skin.award == award)
                )
            ).scalar_one_or_none()

            if skin is None:
                return self.notExists(env, result.group(3)[1:])

            imgUrl = skin.image

            if len(skin.extra_description) > 0:
                desc = skin.extra_description

        return Message(
            [
                at(env.sender),
                text("MSG_ADMIN_DISPLAY"),
                await localImage(imgUrl),
                text(f"\n\n{desc}"),
            ]
        )


@requireAdmin
@dataclass
class CatchAdminObtainSkin(Command):
    commandPattern: str = f":: ?{KEYWORD_OBTAIN} ?{KEYWORD_SKIN}"
    argsPattern: str = " (\\S+) (\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_MODIFY_SKIN_WRONG_FORMAT")])

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

        skin = (
            await env.session.execute(
                select(Skin)
                .filter(Skin.name == result.group(4))
                .filter(Skin.award == award)
            )
        ).scalar_one_or_none()

        if skin is None:
            return self.notExists(env, result.group(4))

        await obtainSkin(env.session, await getSender(env), skin)
        await env.session.commit()

        return modifyOk()


@requireAdmin
@dataclass
class CatchAdminDeleteSkinOwnership(Command):
    commandPattern: str = f":: ?{KEYWORD_REMOVE_OBTAIN} ?{KEYWORD_SKIN}"
    argsPattern: str = " (\\S+) (\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_MODIFY_SKIN_WRONG_FORMAT")])

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

        skin = (
            await env.session.execute(
                select(Skin)
                .filter(Skin.name == result.group(4))
                .filter(Skin.award == award)
            )
        ).scalar_one_or_none()

        if skin is None:
            return self.notExists(env, result.group(4))

        await deleteSkinOwnership(env.session, await getSender(env), skin)
        await env.session.commit()

        return modifyOk()


@requireAdmin
@dataclass
class CatchResetEveryoneCacheCount(Command):
    commandPattern: str = f":: ?{KEYWORD_RESET} ?{KEYWORD_CACHE_COUNT}"
    argsPattern: str = "( (\\d+))?$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_RESET_CACHE_WRONG_FORMAT")])

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        if result.group(4) is None:
            await resetCacheCount(env.session, 1)
            await env.session.commit()
            return Message([at(env.sender), text("MSG_RESET_CACHE_OK")])

        count = int(result.group(4))
        if count < 1:
            return self.errorMessage(env)

        await env.session.commit()
        await resetCacheCount(env.session, count)


@requireAdmin
@dataclass
class CatchAdminHelp(Command):
    commandPattern: str = f":: ?help"
    argsPattern: str = "$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return helpAdmin()


@requireAdmin
@dataclass
class CatchGiveMoney(Command):
    commandPattern: str = ":: ?给钱"
    argsPattern: str = " (\\d+) (-?\\d+)"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text("MSG_GIVE_MONEY_WRONG_FORMAT")])

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        money = int(result.group(2))

        user = await getUser(env.session, int(result.group(1)))
        user.money += money
        await env.session.commit()

        return Message([at(env.sender), text("MSG_GIVE_MONEY_OK")])


@requireAdmin
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
