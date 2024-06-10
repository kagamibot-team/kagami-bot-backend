from dataclasses import dataclass
import math
import time

from sqlalchemy import select

from plugins.passbotqwq.catch.models.Basics import AwardSkin, SkinOwnRecord

from ...putils.command import at, text
from ...putils.draw import imageToBytes

from ..models.crud import (
    getAllLevels,
    getAwardDescriptionOfOneUser,
    getAwardImageOfOneUser,
    getUserUsingSkin,
)
from ..models.data import getPosibilities
from ..models import Award, UserData
from ..cores import PicksResult

from .images import drawCaughtBoxes, drawStatus

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_orm import async_scoped_session

import pathlib


async def displayAward(session: async_scoped_session, award: Award, user: UserData):
    name = award.name
    skin = await getUserUsingSkin(None, user, award)

    if skin is not None:
        name = name + f"[{skin.skin.name}]"

    return Message(
        [
            MessageSegment.text(name + f"【{award.level.name}】"),
            MessageSegment.image(
                pathlib.Path(await getAwardImageOfOneUser(session, user, award))
            ),
            MessageSegment.text(
                f"\n\n{await getAwardDescriptionOfOneUser(session, user, award)}"
            ),
        ]
    )


async def caughtMessage(session: async_scoped_session, picksResult: PicksResult):
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
                MessageSegment.text(f"小哥还没长成，请再等{timeStr}吧！"),
            ]
        )

    ms.append(
        MessageSegment.text(
            f"\n剩余抓小哥次数：{picksResult.restCount}/{maxPick}\n"
            f"下次次数恢复还需{timeStr}\n"
            f"你刚刚一共抓了 {picksResult.counts()} 只小哥，得到了 {picksResult.prizes()} 薯片\n"
            f"现在你一共有 {picksResult.moneyTo()} 薯片"
        )
    )

    image = await drawCaughtBoxes(session, picksResult)
    ms.append(MessageSegment.image(imageToBytes(image)))

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


def help(isAdmin=False):
    normal = [
        "抓小哥帮助(zhuahelp)：显示这条帮助信息",
        "抓小哥(zhua)：进行一次抓",
        "狂抓小哥(kz)：一次抓完所有可用次数",
        "库存(kc)：展示个人仓库中的存量",
        "抓小哥进度(zhuajd)：展示目前收集的进度",
        "设置皮肤 小哥名字 皮肤名字：设置一个小哥的皮肤",
    ]

    # admin = [
    #     "::创建小哥 名字 等级",
    #     "::删除小哥 名字",
    #     "::创建等级 名字",
    #     "::所有等级",
    #     "::所有小哥",
    #     "::设置周期 秒数",
    #     "::更改等级 名称/权重/颜色 等级的名字",
    #     "::更改小哥 名称/等级/图片/描述 小哥的名字",
    #     "::创建皮肤 小哥名字 皮肤名字",
    #     "::更改皮肤 名字/图片/描述 小哥名字 皮肤名字",
    #     "::获得皮肤 小哥名字 皮肤名字",
    #     "::剥夺皮肤 小哥名字 皮肤名字",
    #     "::展示 小哥名字 皮肤名字",
    # ]

    res = normal

    return Message(
        [
            MessageSegment.text(("===== 命令清单 =====\n" + "\n".join(res))),
        ]
    )


def update():
    result: list[str] = []

    for version in updateHistory.keys():
        result.append(
            f"== 版本 {version} 更新 =="
            + "".join(map(lambda x: "\n- " + x, updateHistory[version]))
        )

    return Message(text("\n\n".join(result)))


@dataclass
class Goods:
    code: str
    name: str
    description: str
    price: float
    soldout: bool = False


async def getGoodsList(session: async_scoped_session, user: UserData):
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

    skins = (
        (await session.execute(select(AwardSkin).filter(AwardSkin.price >= 0)))
        .scalars()
        .all()
    )

    for skin in skins:
        isOwned = (
            await session.execute(
                select(SkinOwnRecord)
                .filter(SkinOwnRecord.user == user)
                .filter(SkinOwnRecord.skin == skin)
            )
        ).scalar_one_or_none()

        goods.append(
            Goods(
                "皮肤" + skin.name,
                "购买皮肤 " + skin.name,
                f"小哥 {skin.applied_award.name} 的皮肤 {skin.name}",
                skin.price,
                isOwned is not None,
            )
        )

    return goods


async def KagamiShop(session: async_scoped_session, sender: int, senderUser: UserData):
    textBuilder = f"\n===== 小镜的shop =====\n现在你手上有 {senderUser.money} 薯片\n\n"

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


updateHistory = {
    "0.2.0": [
        "将数据使用数据库储存",
        "修复间隔为 0 时报错的问题",
    ],
    "0.2.1": [
        "修复了一些界面文字没有中心对齐的问题",
        "修复了抓小哥时没有字体颜色的问题",
    ],
    "0.3.0": [
        "正式添加皮肤系统",
        "限制了管理员指令只能在一些群执行",
        "修复了新玩家的周期被设置为 3600 的问题",
        "重新架构了关于图片生成的代码",
    ],
    "0.4.0": [
        "添加了商店系统",
    ]
}
