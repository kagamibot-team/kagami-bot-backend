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


def settingOk():
    return Message(MessageSegment.text("设置好了"))


def modifyOk():
    return Message(MessageSegment.text("更改好了"))
