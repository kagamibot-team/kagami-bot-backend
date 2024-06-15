from dataclasses import dataclass
import re
from sqlalchemy import select
from nonebot.adapters.onebot.v11 import Message

from ..basics import (
    CheckEnvironment,
    at,
    decorateWithLoadingMessage,
    text,
    image,
    Command,
    asyncLock,
    databaseIO,
)

from src.db import *

from ...messages import (
    drawStatus,
    drawStorage,
    KagamiShop,
    getGoodsList,
)
from ...messages.lang import *

from .keywords import *
from .tools import getSender


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
