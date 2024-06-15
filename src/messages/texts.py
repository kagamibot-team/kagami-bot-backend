from dataclasses import dataclass
import time

from nonebot import logger
from sqlalchemy import select


from ..commands.basics import at, text
from ..utils.draw import imageToBytes

from models.base import *
from models import *
from ..db.crud import *
from ..db.data import *
from ..images import *

from .images import drawStatus

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session


Session = async_scoped_session | AsyncSession


def createLevelWrongFormat():
    return Message(
        MessageSegment.text(
            "你的格式有问题，应该是 ::创建等级 名字 权重 价值 (可选)颜色Hue(0-360)"
        )
    )


def deleteLevelWrongFormat():
    return Message(MessageSegment.text("你的格式有问题，应该是 ::删除等级 名字"))


def setIntervalWrongFormat():
    return Message(MessageSegment.text("你的格式有问题，应该是 ::设置周期 秒数"))


def displayWrongFormat():
    return Message(MessageSegment.text("你的格式有问题，应该是 展示 类型"))


def noAwardNamed(name: str):
    return Message(MessageSegment.text(f"没有叫做 {name} 的小哥"))


async def allLevels(session: async_scoped_session):
    begin = time.time()
    levelObjs = (await session.execute(select(Level))).scalars().all()
    logger.debug("查询所有 Level 花费了 %.2f 秒" % (time.time() - begin))

    levels = [
        f"\n- 【{l.name}】权重 {l.weight} 爆率 {round((await getPosibilities(session, l)) * 100, 2)} %"
        for l in levelObjs
        if l.name != "名称已丢失"
    ]

    return Message(MessageSegment.text("所有包含的等级：" + "".join(levels)))


async def allAwards(session: async_scoped_session):
    _levels = await getAllLevels(session)

    _result: list[str] = []

    for level in _levels:
        _awards = level.awards

        if len(_awards) == 0:
            continue

        if level.name == "名称已丢失":
            continue

        _result.append(
            f"【{level.name}】爆率: {await getPosibilities(session, level) * 100}%\n"
            + "，".join([award.name for award in _awards])
        )

    result = "\n\n".join(_result)

    image = await drawStatus(session, None)

    return Message(
        [
            MessageSegment.text("===== 奖池 =====\n" + result),
            MessageSegment.image(imageToBytes(image)),
        ]
    )


def settingOk():
    return Message(MessageSegment.text("设置好了"))


def modifyOk():
    return Message(MessageSegment.text("更改好了"))


@dataclass
class Goods:
    code: str
    name: str
    description: str
    price: float
    soldout: bool = False


async def getGoodsList(session: async_scoped_session, user: User):
    goods: list[Goods] = []

    cacheDelta = user.pick_max_cache + 1
    goods.append(
        Goods(
            "加上限",
            f"增加卡槽至 {cacheDelta}",
            f"将囤积可以抓的小哥的数量上限增加至 {cacheDelta}",
            25 * (2 ** (cacheDelta - 1)),
        )
    )

    skins = await getAllSkinsSelling(session)

    for skin in skins:
        isOwned = await getOwnedSkin(session, user, skin)

        goods.append(
            Goods(
                "皮肤" + skin.name,
                "购买皮肤 " + skin.name,
                f"小哥 {skin.award.name} 的皮肤 {skin.name}",
                skin.price,
                isOwned is not None,
            )
        )

    return goods


async def KagamiShop(session: async_scoped_session, sender: int, senderUser: User):
    textBuilder = f"\n===== 小镜的shop =====\n现在你手上有 {senderUser.money} 薯片\n输入 小镜的shop 购买 商品码 就可以买了哦\n\n"

    goodTexts: list[str] = []

    for good in await getGoodsList(session, senderUser):
        soldoutMessage = "[售罄] " if good.soldout else ""

        goodTexts.append(
            f"{soldoutMessage}{good.name}\n"
            f"- {good.description}\n"
            f"- 商品码：{good.code}\n"
            f"- 价格：{good.price} 薯片\n"
        )

    textBuilder += "\n".join(goodTexts)

    return Message([at(sender), text(textBuilder)])
