from dataclasses import dataclass
import re
from sqlalchemy import select
from nonebot.adapters.onebot.v11 import Message

from ..classes import (
    CheckEnvironment,
    at,
    decorateWithLoadingMessage,
    text,
    image,
    Command,
    asyncLock,
    databaseIO,
)

from ...models import *

from ...messages import (
    caughtMessage,
    help,
    displayAward,
    drawStatus,
    drawStorage,
    KagamiShop,
    getGoodsList,
    update,
)
from ...messages.lang import *

from .keywords import *
from .tools import getSender


@decorateWithLoadingMessage(MSG_CATCH_LOADING)
@asyncLock()
@databaseIO()
@dataclass
class Catch(Command):
    commandPattern: str = f"^{KEYWORD_BASE_COMMAND} ?(\\d+)?"
    argsPattern: str = "$"

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        maxCount = 1

        if result.group(2) is not None and result.group(2).isdigit():
            maxCount = int(result.group(2))
        
        picksResult = await handlePick(env.session, env.sender, maxCount)
        message = await caughtMessage(env.session, await getSender(env), picksResult)

        return message


@decorateWithLoadingMessage(MSG_CATCH_LOADING)
@asyncLock()
@databaseIO()
@dataclass
class CrazyCatch(Command):
    commandPattern: str = f"^({KEYWORD_CRAZY}{KEYWORD_BASE_COMMAND}|kz)"
    argsPattern: str = "$"

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        picksResult = await handlePick(env.session, env.sender, -1)

        message = await caughtMessage(env.session, await getSender(env), picksResult)

        return message


@dataclass
class CatchHelp(Command):
    commandPattern: str = f"^{KEYWORD_BASE_COMMAND}? ?{KEYWORD_HELP}"
    argsPattern: str = "$"

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        return help()


@decorateWithLoadingMessage(MSG_STORAGE_LOADING)
@dataclass
class CatchStorage(Command):
    commandPattern: str = f"^{KEYWORD_BASE_COMMAND}?{KEYWORD_STORAGE}"
    argsPattern: str = "$"

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        storageImage = await drawStorage(env.session, await getSender(env))

        return Message(
            [
                at(env.sender),
                text(MSG_STORAGE),
                await image(storageImage),
            ]
        )


@decorateWithLoadingMessage(MSG_STATUS_LOADING)
@dataclass
class CatchProgress(Command):
    commandPattern: str = f"^{KEYWORD_BASE_COMMAND} ?{KEYWORD_PROGRESS} ?"
    argsPattern: str = "$"

    async def check(self, env: CheckEnvironment) -> Message | None:
        return await super().check(env)

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


@dataclass
class CatchDisplay(Command):
    commandPattern: str = f"^{KEYWORD_DISPLAY} ?{KEYWORD_AWARDS}? "
    argsPattern: str = "(\\S+)$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        name = result.group(3)
        award = await getAwardByName(env.session, name)

        if award is None:
            return Message([at(env.sender), text(f" 你没有名字叫 {name} 的小哥")])

        ac = await getStorage(env.session, await getSender(env), award)

        if ac.count <= 0:
            return Message([at(env.sender), text(f" 你没有名字叫 {name} 的小哥")])

        return await displayAward(env.session, award, await getSender(env))


@asyncLock()
@databaseIO()
@dataclass
class CatchHangUpSkin(Command):
    commandPattern: str = f"{KEYWORD_SWITCH} ?{KEYWORD_SKIN}"
    argsPattern: str = " (\\S+)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message([at(env.sender), text(" 格式不对，格式是 切换皮肤 小哥名字")])

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        award = await getAwardByName(env.session, result.group(3))

        if award is None:
            return self.notExists(env, result.group(3))

        skins = await getAllOwnedSkin(env.session, await getSender(env), award)

        if len(skins) == 0:
            return Message([at(env.sender), text(" 你没有这个小哥的皮肤")])

        skin = await switchSkin(
            env.session, await getSender(env), [s.skin for s in skins], award
        )

        if skin is not None:
            message = Message(
                [
                    at(env.sender),
                    text(f" 已经将 {result.group(3)} 的皮肤切换为 {skin.name} 了"),
                ]
            )
        else:
            message = Message(
                [at(env.sender), text(f" 已经将 {result.group(3)} 的皮肤切换为默认了")]
            )

        return message


@dataclass
class CatchShowUpdate(Command):
    commandPattern: str = f"^{KEYWORD_BASE_COMMAND} ?{KEYWORD_UPDATE}"
    argsPattern: str = "$"

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        return update()


@asyncLock()
@databaseIO()
@dataclass
class CatchShop(Command):
    commandPattern: str = f"^{KEYWORD_KAGAMIS} ?{KEYWORD_SHOP}"
    argsPattern: str = "(.*)$"

    def errorMessage(self, env: CheckEnvironment) -> Message | None:
        return Message(
            [
                at(env.sender),
                text(
                    " \n小镜的 shop 指令：\n"
                    "- 小镜的shop: 查看商品\n"
                    "- 小镜的shop 购买 商品码: 购买商品"
                ),
            ]
        )

    async def handleCommand(
        self, env: CheckEnvironment, result: re.Match[str]
    ) -> Message | None:
        args = [r for r in result.group(3).split(" ") if len(r) > 0]

        if len(args) == 0:
            return await KagamiShop(env.session, env.sender, await getSender(env))

        if len(args) == 2:
            if args[0] == "购买":
                code = args[1]
                goods = await getGoodsList(env.session, await getSender(env))

                if code not in [g.code for g in goods]:
                    return self.notExists(env, code)

                good = [g for g in goods if g.code == code][0]

                if good.soldout:
                    return Message(
                        [at(env.sender), text(f" 商品 {good.name} 已经卖完了哦")]
                    )

                user = await getSender(env)

                if good.price > user.money:
                    return Message(
                        [
                            at(env.sender),
                            text(
                                f" 你的薯片不够了，商品 {good.name} 需要 {good.price} 薯片"
                            ),
                        ]
                    )

                await buy(env.session, user, code, good.price)

                moneyLeft = user.money

                return Message(
                    [
                        at(env.sender),
                        text(f" 购买 {good.name} 成功！你还剩下 {moneyLeft} 薯片"),
                    ]
                )

        return self.errorMessage(env)


@dataclass
class CatchCheckMoney(Command):
    commandPattern: str = f"^(我有多少薯片|mysp)"
    argsPattern: str = "$"

    async def handleCommand(self, env: CheckEnvironment, result: re.Match[str]):
        user = await getSender(env)
        return Message([at(env.sender), text(f" 你有 {user.money} 薯片")])
