import time

from nonebot import logger
from sqlalchemy import select

from ..db.crud import *
from ..db.data import *
from src.components import *

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import *


Session = AsyncSession


def setIntervalWrongFormat():
    return Message(MessageSegment.text("你的格式有问题，应该是 ::设置周期 秒数"))


async def allLevels(session: AsyncSession):
    begin = time.time()
    levelObjs = (await session.execute(select(Level))).scalars().all()
    logger.debug("查询所有 Level 花费了 %.2f 秒" % (time.time() - begin))

    levels = [
        f"\n- 【{l.name}】权重 {l.weight} 爆率 {round((await getPosibilities(session, l)) * 100, 2)} %"
        for l in levelObjs
        if l.name != "名称已丢失"
    ]

    return Message(MessageSegment.text("所有包含的等级：" + "".join(levels)))


def settingOk():
    return Message(MessageSegment.text("设置好了"))


def modifyOk():
    return Message(MessageSegment.text("更改好了"))
