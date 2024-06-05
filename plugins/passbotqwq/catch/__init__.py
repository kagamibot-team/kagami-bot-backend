import asyncio
from nonebot.plugin import on
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.exception import FinishedException
from typing import NoReturn
import re

from ..putils.download import download, writeData
from ..putils.text_format_check import (
    checkFormat,
    isFloat,
    regex,
    ok,
    not_negative,
)

from .models import UserData, Award, GameGlobalConfig, Level
from .data import getAwardByAwardName, getImageTarget, globalData, userData, save
from .messages import (
    addAward2,
    addAward3,
    createLevelWrongFormat,
    deleteLevelWrongFormat,
    displayAward,
    displayWrongFormat,
    noAwardNamed,
    addAward1,
)
from .commands import CallbackBase, CheckEnvironment, WaitForMoreInformationException, enabledCommand


eventMatcher = on()


async def finish(message: Message) -> NoReturn:
    await eventMatcher.finish(message)


flag: dict[int, int] = {}

callbacks: dict[int, CallbackBase | None] = {}

award_create_tmp: dict[int, Award] = {}

WHITELIST_NO_WUM = ["136468747", "963431993"]


def getFlag(uid: int):
    if uid not in flag.keys():
        flag[uid] = 0

    return flag[uid]


def getCallbacks(uid: int):
    if uid not in callbacks.keys():
        callbacks[uid] = None
    
    return callbacks[uid]


async def handleSpecial(sender: int, event: GroupMessageEvent):
    if getFlag(sender) == 1:
        text = event.get_plaintext()
        if text == "::cancel":
            flag[sender] = 0
            await finish(Message(MessageSegment.text("已取消")))

        if len(text) == 0 or " " in text:
            await finish(Message(MessageSegment.text("请重新输入一个名字吧")))

        if globalData.get().containAwardName(text):
            await finish(
                Message(MessageSegment.text("名字已存在，请重新选择一个名字吧"))
            )

        award_create_tmp[sender].name = text
        flag[sender] = 2

        await asyncio.sleep(0.2)
        await finish(
            addAward2(award_create_tmp[sender]),
        )

    if getFlag(sender) == 2:
        text = event.get_plaintext()

        if text == "::cancel":
            flag[sender] = 0
            await finish(Message(MessageSegment.text("已取消")))

        if text == "::rev":
            flag[sender] = 1
            await finish(addAward1())

        if text.isdigit() and globalData.get().isLevelIdExists(int(text)):
            award_create_tmp[sender].levelId = int(text)
            flag[sender] = 3

            await finish(
                addAward3(award_create_tmp[sender]),
            )

        await finish(Message(MessageSegment.text("请重新输入一个数字")))

    if getFlag(sender) == 3:
        text = event.get_plaintext()

        if text == "::cancel":
            flag[sender] = 0
            await finish(Message(MessageSegment.text("已取消")))

        if text == "::rev":
            flag[sender] = 2
            await finish(addAward2(award_create_tmp[sender]))

        if len(event.get_message().include("image")) != 1:
            await finish(
                Message(MessageSegment.text("没有识别到图片，请重新发送一个图片吧"))
            )

        image = event.get_message().include("image")[0]

        if "type" in image.data.keys() and image.data["type"] == "flash":
            await finish(Message(MessageSegment.text("别发闪照，麻烦再发一张吧")))

        fp = getImageTarget(award_create_tmp[sender])

        await writeData(await download(image.data["url"]), fp)
        award_create_tmp[sender].updateImage(fp)

        with globalData as d:
            aid = d.addAward(
                award_create_tmp[sender].name,
                award_create_tmp[sender].levelId,
                award_create_tmp[sender].imgPath,
            )

        print(f"CREATED AWARD (ID = {aid})")

        flag[sender] = 0
        await finish(Message(MessageSegment.text("创建成功！")))

    flag[sender] = 0
    await finish(Message(MessageSegment.text("遇到了未知的情况，已初始化")))


@eventMatcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    sender = event.sender.user_id

    if sender == None:
        return
    assert type(sender) == int

    if getFlag(sender) != 0:
        await handleSpecial(sender, event)
        return

    text = event.get_plaintext()

    if re.match("^::(添加|增加|创建|新建|新增)小哥$", text):
        flag[sender] = 1
        award_create_tmp[sender] = Award()
        await finish(addAward1())

    env = CheckEnvironment(sender, text, event.message_id, event.message)

    callback = getCallbacks(sender)
    if callback != None:
        try:
            message = await callback.check(env)
        except WaitForMoreInformationException as e:
            callbacks[sender] = e.callback
            if e.message is not None:
                await finish(e.message)
            raise FinishedException()

        callbacks[sender] = None
        
        if message:
            await finish(message)
        
        raise FinishedException()

    for command in enabledCommand:
        try:
            res = await command.check(env)
        except WaitForMoreInformationException as e:
            callbacks[sender] = e.callback
            if e.message is not None:
                await finish(e.message)
            raise FinishedException()

        if res:
                await finish(res)

    if text.startswith("::删除小哥"):
        if len(text.split(" ")) == 2:
            with globalData as d:
                awardList = d.removeAwardsByName(text.split("::删除小哥 ")[1])

            if len(awardList) == 0:
                await finish(
                    Message(MessageSegment.text("删除失败，因为没有这个名字的小哥"))
                )
            await finish(Message(MessageSegment.text("已经删除了")))
        await finish(
            Message(MessageSegment.text("你的格式有问题，应该是 ::删除小哥 小哥的名字"))
        )

    if re.match("^::(添加|增加|创建|新建|新增)等级", text):
        if not checkFormat(
            text, [ok(), ok(), not_negative(), not_negative()], [isFloat()]
        ):
            await finish(createLevelWrongFormat())

        args = text.split(" ")

        if len([l for l in globalData.get().levels if l.name == args[1]]) > 0:
            await finish(Message(MessageSegment.text("存在一个相同名字的等级")))

        with globalData as d:
            _arg4 = float(args[4]) if len(args) == 5 else 0
            d.addLevel(args[1], float(args[2]), float(args[3]), _arg4)

        save()
        await finish(Message(MessageSegment.text("创建成功！")))

    if text.startswith("::删除等级"):
        await finish(Message(MessageSegment.text("这个函数没写完先别用")))
        if len(text.split(" ")) == 2:
            args = text.split(" ")

            removed = globalData.get().removeLevelByName(args[1])

            if len(removed) == 0:
                await finish(
                    Message(MessageSegment.text("删除失败，因为不存在这个名字的等级"))
                )

            save()
            await finish(Message(MessageSegment.text("删除成功")))

        await finish(deleteLevelWrongFormat())

    if text == "抓wum" and str(event.group_id) in WHITELIST_NO_WUM:
        await finish(Message(MessageSegment.text("别抓 wum 了，来「抓抓」吧")))

    if regex("^(展示|disp|display)")(text):
        if not checkFormat(text, [ok(), ok()]):
            await finish(displayWrongFormat())

        args = text.split(" ")
        award = getAwardByAwardName(args[1])

        if len(award) == 0:
            await finish(noAwardNamed(args[1]))

        await finish(displayAward(award[0]))
