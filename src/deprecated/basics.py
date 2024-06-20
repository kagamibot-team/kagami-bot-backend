from dataclasses import dataclass
import re
from nonebot.adapters.onebot.v11 import Message

from .old_version import (
    CheckEnvironment,
    at,
    text,
    Command,
    asyncLock,
    databaseIO,
)

from .db import *
from .messages import *
from .messages.lang import *

from .keywords import *
from .tools import getSender


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
