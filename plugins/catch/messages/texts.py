from dataclasses import dataclass
import math
import time


from ..putils.command import at, image, text
from ..putils.draw import imageToBytes

from ..models import *
from ..images import *

from .images import drawCaughtBoxes, drawStatus

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_orm import async_scoped_session

import pathlib


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
                MessageSegment.text(f" 小哥还没长成，请再等{timeStr}吧！"),
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

    ## 新版界面
    image = await drawCaughtBoxes(session, picksResult)
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


def help():
    normal = [
        "抓小哥帮助(zhuahelp)：显示这条帮助信息",
        "抓小哥(zhua)：进行一次抓",
        "狂抓小哥(kz)：一次抓完所有可用次数",
        "库存(kc)：展示个人仓库中的存量",
        "抓小哥进度(zhuajd)：展示目前收集的进度",
        "切换皮肤 小哥名字：切换一个小哥的皮肤",
        "小镜的shop(xjshop)：进入小镜的商店",
        "我有多少薯片(mysp)：告诉你你有多少薯片",
    ]

    res = normal

    return Message(
        [
            MessageSegment.text(("===== 命令清单 =====\n" + "\n".join(res))),
        ]
    )


def helpAdmin():
    res = [
        "::所有小哥",
        "::所有等级",
        "::设置周期 秒数",
        "::设置小哥 名称/图片/等级/描述 小哥的名字",
        "::设置等级 名称/权重/颜色/金钱/优先 等级的名字 值",
        "::删除小哥 小哥的名字",
        "::创建小哥 名字 等级",
        "::创建等级 名字",
        "/give qqid 小哥的名字 (数量)",
        "/clear (qqid (小哥的名字))",
        "::创建皮肤 小哥名字 皮肤名字",
        "::更改皮肤 名字/图片/描述/价格 皮肤名字",
        "::获得皮肤 皮肤名字",
        "::剥夺皮肤 皮肤名字",
        "::展示 小哥名字 (皮肤名字)",
        "::重置抓小哥上限（注意这个是对所有人生效的）",
        "::给钱 qqid 钱",
        "::添加小哥/等级/皮肤别称 原名 别称",
        "::删除小哥/等级/皮肤别称 别称",
    ]

    return Message(
        [
            MessageSegment.text(("===== 命令清单 =====\n" + "\n".join(res))),
        ]
    )


def update():
    result: list[str] = []

    for version in list(updateHistory.keys())[::-1][:5]:
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


updateHistory: dict[str, list[str]] = {
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
    ],
    "0.4.1": [
        "将版本更新信息倒序而非正序显示",
        "调整了库存的显示顺序",
        "新抓到小哥能够获得奖励了",
        "来・了（数据恢复）",
    ],
    "0.4.2": [
        "热更新：修复了新用户有关的各种小问题",
    ],
    "0.4.3": [
        "修复了无法应用多个皮肤的问题",
        "调整了图片编码器以加快图片的生成速度",
    ],
    "0.4.4": [
        "调整了抓小哥进度中等级显示的顺序",
        "修复了可以靠刷屏多次抓小哥的 BUG",
    ]
}
