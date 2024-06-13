from dataclasses import dataclass
import math
import time


from ..commands.basics import at, image, text
from ..putils.draw import imageToBytes

from ..models import *
from ..images import *

from .images import drawCaughtBoxes_, drawStatus

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_orm import AsyncSession, async_scoped_session, get_session

import pathlib


Session = async_scoped_session | AsyncSession


async def displayAward(session: async_scoped_session, award: Award, user: User):
    name = award.name
    skin = await getUsedSkin(session, user, award)

    if skin is not None:
        name = name + f"[{skin.skin.name}]"

    return Message(
        [
            MessageSegment.text(name + f"【{award.level.name}】"),
            MessageSegment.image(
                pathlib.Path(await getAwardImage(session, user, award))
            ),
            MessageSegment.text(
                f"\n\n{await getAwardDescription(session, user, award)}"
            ),
        ]
    )


async def caughtMessage(picksResult: PicksResult):
    ms = [MessageSegment.at(picksResult.uid)]
    maxPick = picksResult.max_pick
    delta = picksResult.time_delta

    nextTime = picksResult.pick_calc_time + delta

    deltaTime = math.ceil(nextTime - time.time())

    seconds = deltaTime % 60
    minutes = int(deltaTime / 60) % 60
    hours = int(deltaTime / 3600)

    timeStr = f"{seconds}秒"
    if hours > 0:
        timeStr = f"{hours}小时{minutes}分钟" + timeStr
    elif minutes > 0:
        timeStr = f"{minutes}分钟" + timeStr

    if picksResult.counts() == 0:
        return Message(
            [
                MessageSegment.at(picksResult.uid),
                MessageSegment.text(f" 小哥还没长成，请再等{timeStr}吧！"),
            ]
        )

    tx = (
        f"\n剩余抓小哥次数：{picksResult.restCount}/{maxPick}\n"
        f"下次次数恢复还需{timeStr}\n"
        f"你刚刚一共抓了 {picksResult.counts()} 只小哥，得到了 {picksResult.prizes()} 薯片\n"
        f"现在你一共有 {picksResult.moneyTo()} 薯片\n"
    )

    session = get_session()

    async with session.begin():
        if picksResult.baibianxiaogeOccured:
            skinId = picksResult.baibianxiaogeSkin

            if skinId is not None:
                skin = await getSkinById(session, skinId)
                await setSkin(session, await picksResult.dbUser(session), skin)

                tx += f"\n在这些小哥之中，你抓到了一只 {skin.name}！\n"
            else:
                tx += f"\n在这些小哥之中，你抓到了一只百变小哥，但是它已经没辙了，只会在你面前装嫩了。\n"

        ms.append(MessageSegment.text(tx))

        ## 新版界面
        image = await drawCaughtBoxes_(session, picksResult)
        ms.append(MessageSegment.image(imageToBytes(image)))

        ## 旧版界面
        # user = ...

        # for p in picksResult.picks:
        #     award = ...
        #     level = award.level

        #     ms.append(await image(await display_box(
        #         level.level_color_code,
        #         await getAwardImageOfOneUser(session, user, award),
        #         p.isNew()
        #     )))

        #     ms.append(text(
        #         f"【{level.name}】{award.name}\n"
        #         f"{await getAwardDescriptionOfOneUser(session, user, award)}\n"
        #     ))

    return Message(ms)


def cannotGetAward(userId: int, delta: float):
    hours = math.floor(delta / 3600)
    minutes = math.floor(delta / 60) % 60
    seconds = round((math.ceil(delta * 1000) / 1000) % 60, 2)

    return Message(
        [
            MessageSegment.at(userId),
            MessageSegment.text(
                f"还需要 {hours} 小时 {minutes} 分钟 {seconds} 秒你才能抓哦"
            ),
        ]
    )


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
    levelObjs = await getAllLevels(session)

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
