import math
from .models import Award
from .data import (
    getAllLevels,
    getAwardsFromLevelId,
    getLevelNameOfAward,
    getPosibilities,
    globalData,
    userData,
)

from nonebot.adapters.onebot.v11 import Message, MessageSegment

import pathlib


def getAward(userId: int, award: Award):
    return Message(
        [
            MessageSegment.at(userId),
            MessageSegment.text(" 你刚刚抓到了一只：" + award.name + "！"),
            MessageSegment.image(pathlib.Path(award.imgPath)),
            MessageSegment.text(
                "稀有度：" + globalData.get().getLevelByLid(award.levelId).name
            ),
        ]
    )


def displayAward(award: Award):
    return Message(
        [
            MessageSegment.text("展示 " + award.name),
            MessageSegment.image(pathlib.Path(award.imgPath)),
            MessageSegment.text(
                "稀有度：" + globalData.get().getLevelByLid(award.levelId).name
            ),
        ]
    )


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


def storageCheck(userId: int):
    if userData.get(userId).getAwardSum() == 0:
        return Message(
            [MessageSegment.at(userId), MessageSegment.text("你的仓库里什么也没有～")]
        )

    ac = userData.get(userId).awardCounter

    return Message(
        [
            MessageSegment.at(userId),
            MessageSegment.text(
                "你的仓库的库存如下：\n -"
                + "\n -".join(
                    [
                        f"「{globalData.get().getAwardByAidStrong(a).name}」共有 {ac[a]} 个"
                        for a in ac.keys()
                        if ac[a] > 0 and globalData.get().haveAid(a)
                    ]
                )
            ),
        ]
    )


def addAward1():
    return Message(MessageSegment.text("(输入 ::cancel 取消)\n请输入奖品名称: >_<"))


def addAward2(awardTemp: Award):
    levels = [f"{level.lid} - {level.name}" for level in globalData.get().levels if level.name != '名称已丢失']

    return Message(
        MessageSegment.text(
            "".join(
                (
                    "(输入 ::cancel 取消)\n",
                    "(输入 ::rev 回到上一步)\n",
                    f"请输入奖品名称: {awardTemp.name}\n",
                    "请输入奖品等级 (数字)): >_<\n(",
                    "; ".join(levels),
                    ")",
                )
            )
        )
    )


def addAward3(awardTemp: Award):
    level = globalData.get().getLevelByLid(awardTemp.levelId)

    return Message(
        MessageSegment.text(
            (
                "(输入 ::cancel 取消)\n"
                "(输入 ::rev 回到上一步)\n"
                f"请输入奖品名称: {awardTemp.name}\n"
                f"请输入奖品等级 (数字)): {level.name}\n"
                "请发送一张图片: >_<"
            )
        )
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
    return Message(MessageSegment.text(f"没有叫做 {name} 的奖品"))


def allLevels():
    levels = [f"[{l.name}] 权重 {l.weight}" for l in globalData.get().levels]

    return Message(MessageSegment.text("所有包含的等级：\n- " + "\n- ".join(levels)))


def allAwards():
    _levels = getAllLevels()

    _result: list[str] = []

    for level in _levels:
        _awards = getAwardsFromLevelId(level.lid)

        if len(_awards) == 0:
            continue

        if level.name == '名称已丢失':
            continue

        _result.append(
            f"【{level.name}】爆率: {getPosibilities(level)}%\n" + "，".join([award.name for award in _awards])
        )

    result = "\n\n".join(_result)

    return Message(MessageSegment.text("===== 奖池 =====\n" + result))


def settingOk():
    return Message(MessageSegment.text("设置好了"))


def modifyOk():
    return Message(MessageSegment.text("更改好了"))


def help():
    return Message(
        [
            MessageSegment.text(
                (
                    "命令清单：\n"
                    "- 抓抓\n"
                    "- 抓抓帮助\n"
                    "- 库存\n"
                    "- ::创建奖品\n"
                    "- ::删除奖品 名字\n"
                    "- ::创建等级 名字 权重 价值\n"
                    "- ::删除等级 名字\n"
                    "- ::所有等级\n"
                    "- ::所有奖品\n"
                    "- ::设置周期 秒数\n"
                    "- ::更改等级 名称/权重 等级的名字\n"
                    "- ::更改奖品 名称/等级/图片 奖品的名字"
                )
            ),
        ]
    )
