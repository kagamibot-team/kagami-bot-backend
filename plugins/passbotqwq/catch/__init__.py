import asyncio
import os
import time
from nonebot.plugin import on
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from typing import Any
import uuid
import re

from ..putils.download import download, writeData
from ..putils.text_format_check import (
    checkFormat,
    combine,
    isDigit,
    isFloat,
    literal,
    regex,
    ok,
    not_negative,
    matchCommand,
)

from .models import UserData, Award, GameGlobalConfig, Level
from .data import getAwardByAwardName, globalData, userData, save
from .messages import (
    addAward2,
    addAward3,
    allAwards,
    allLevels,
    cannotGetAward,
    createLevelWrongFormat,
    deleteLevelWrongFormat,
    displayAward,
    displayWrongFormat,
    getAward,
    help,
    noAwardNamed,
    setIntervalWrongFormat,
    storageCheck,
    addAward1,
)


eventMatcher = on()

flag: dict[int, int] = {}

award_create_tmp: dict[int, Award] = {}

WHITELIST_NO_WUM = ["136468747", "963431993"]


def getFlag(uid: int):
    if uid not in flag.keys():
        flag[uid] = 0

    return flag[uid]


async def handleSpecial(sender: int, bot: Bot, event: GroupMessageEvent):
    if getFlag(sender) == 1:
        text = event.get_plaintext()
        if text == "::cancel":
            flag[sender] = 0
            await eventMatcher.finish("已取消")

        if len(text) == 0 or " " in text:
            await eventMatcher.finish("请重新输入一个名字吧")

        if globalData.get().containAwardName(text):
            await eventMatcher.finish("名字已存在，请重新选择一个名字吧")

        award_create_tmp[sender].name = text
        flag[sender] = 2

        await asyncio.sleep(0.2)
        await eventMatcher.finish(
            addAward2(award_create_tmp[sender]),
        )

    if getFlag(sender) == 2:
        text = event.get_plaintext()

        if text == "::cancel":
            flag[sender] = 0
            await eventMatcher.finish("已取消")

        if text == "::rev":
            flag[sender] = 1
            await eventMatcher.finish(addAward1())

        if text.isdigit() and globalData.get().isLevelIdExists(int(text)):
            award_create_tmp[sender].levelId = int(text)
            flag[sender] = 3

            await eventMatcher.finish(
                addAward3(award_create_tmp[sender]),
            )

        await eventMatcher.finish("请重新输入一个数字")

    if getFlag(sender) == 3:
        text = event.get_plaintext()

        if text == "::cancel":
            flag[sender] = 0
            await eventMatcher.finish("已取消")

        if text == "::rev":
            flag[sender] = 2
            await eventMatcher.finish(addAward2(award_create_tmp[sender]))

        if len(event.get_message().include("image")) != 1:
            await eventMatcher.finish("没有识别到图片，请重新发送一个图片吧")

        image = event.get_message().include("image")[0]

        if "type" in image.data.keys() and image.data["type"] == "flash":
            await eventMatcher.finish("别发闪照，麻烦再发一张吧")

        fp = os.path.join(os.getcwd(), "data", "catch", f"award_{uuid.uuid4().hex}.png")

        await writeData(await download(image.data["url"]), fp)
        award_create_tmp[sender].updateImage(fp)

        aid = globalData.get().addAward(
            award_create_tmp[sender].name,
            award_create_tmp[sender].levelId,
            award_create_tmp[sender].imgPath,
        )

        print(f"CREATED AWARD (ID = {aid})")

        save()
        flag[sender] = 0
        await eventMatcher.finish("创建成功！")

    flag[sender] = 0
    await eventMatcher.finish("遇到了未知的情况，已初始化")


@eventMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if bot.self_id != "3687050325":
        return

    sender = event.sender.user_id

    if sender == None:
        return
    assert type(sender) == int

    if getFlag(sender) != 0:
        await handleSpecial(sender, bot, event)
        return

    text = event.get_plaintext()

    if regex("^(抓抓|zz)$")(text):
        tm = time.time()
        delta = userData.get(sender).lastCatch + globalData.get().timeDelta - tm

        if delta > 0:
            await eventMatcher.finish(
                cannotGetAward(
                    sender,
                    userData.get(sender).lastCatch + globalData.get().timeDelta - tm,
                ),
            )

        award = globalData.get().pick()

        with userData.open(sender) as d:
            d.addAward(award.aid)
            d.lastCatch = tm

        await eventMatcher.finish(getAward(sender, award))

    if regex("^(抓抓|zz) ?(help|帮助)$")(text):
        await eventMatcher.finish(help())

    if regex("^(抓抓|zz)?(库存|kc)$")(text):
        await eventMatcher.finish(storageCheck(sender))

    if re.match("^::(添加|增加|创建|新建|新增)奖品$", text):
        flag[sender] = 1
        award_create_tmp[sender] = Award()
        await eventMatcher.finish(addAward1())

    if text.startswith("::删除奖品"):
        if len(text.split(" ")) == 2:
            awardList = globalData.get().removeAwardsByName(
                text.split("::删除奖品 ")[1]
            )
            if len(awardList) == 0:
                await eventMatcher.finish("删除失败，因为没有这个名字的奖品")
            await eventMatcher.finish("已经删除了")
        await eventMatcher.finish("你的格式有问题，应该是 ::删除奖品 奖品的名字")

    if re.match("^::(添加|增加|创建|新建|新增)等级", text):
        if not checkFormat(
            text, [ok(), ok(), not_negative(), not_negative()], [isFloat()]
        ):
            await eventMatcher.finish(createLevelWrongFormat())

        args = text.split(" ")

        if len([l for l in globalData.get().levels if l.name == args[1]]) > 0:
            await eventMatcher.finish("存在一个相同名字的等级")
        
        with globalData as d:
            _arg4 = float(args[4]) if len(args) == 5 else 0
            d.addLevel(
                args[1], float(args[2]), float(args[3]), _arg4
            )

        save()
        await eventMatcher.finish("创建成功！")

    if text.startswith("::删除等级"):
        if len(text.split(" ")) == 2:
            args = text.split(" ")

            removed = globalData.get().removeLevelByName(args[1])

            if len(removed) == 0:
                await eventMatcher.finish("删除失败，因为不存在这个名字的等级")

            save()
            await eventMatcher.finish("删除成功")

        await eventMatcher.finish(deleteLevelWrongFormat())

    if text == "::所有等级":
        await eventMatcher.finish(allLevels())

    if text == "::所有奖品":
        await eventMatcher.finish(allAwards())

    if text.startswith("::设置周期"):
        if not checkFormat(text, [ok(), isFloat()]):
            await eventMatcher.finish(setIntervalWrongFormat())

        args = text.split(" ")
        globalData.get().timeDelta = float(args[1])
        save()
        await eventMatcher.finish("设置好了")

    if text == "抓wum" and str(event.group_id) in WHITELIST_NO_WUM:
        await eventMatcher.finish(MessageSegment.text("别抓 wum 了，来「抓抓」吧"))

    if text == "::cheat":
        award = globalData.get().getAwardByAidStrong(7)
        userData.set(sender, userData.get(sender).addAward(award.aid))
        save()
        await eventMatcher.finish(getAward(sender, award))

    if regex("^(展示|disp|display)")(text):
        if not checkFormat(text, [ok(), ok()]):
            await eventMatcher.finish(displayWrongFormat())
        
        args = text.split(' ')
        award = getAwardByAwardName(args[1])

        if len(award) == 0:
            await eventMatcher.finish(noAwardNamed(args[1]))

        await eventMatcher.finish(displayAward(award[0]))

        
