from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.dataclasses.user import UserTime


@dataclass
class Pick:
    """
    单条抓小哥的记录
    """

    beforeStats: int
    delta: int


@dataclass
class Picks:
    """
    一个记录抓小哥结果的数据类，仅储存在内存中，可以在后续流程中更改其中的结果。
    """

    awards: dict[int, Pick]
    money: float


@dataclass
class PicksEvent:
    """
    抓小哥事件，在抓小哥之后、库存数据写入数据库之前时触发的事件
    """

    uid: int
    picks: Picks
    session: AsyncSession


@dataclass
class PickDisplay:
    """
    将会呈交给图像渲染的一行「抓到了」的信息
    """

    name: str
    image: str
    description: str
    level: str
    color: str
    beforeStorage: int
    pick: Pick


@dataclass
class PrePickMessageEvent:
    """
    在抓小哥数据库存写入之后、关闭数据库并构建返回给用户的消息之前触发的事件
    """

    picks: Picks
    displays: dict[int, PickDisplay]
    uid: int
    session: AsyncSession
    userTime: UserTime
    moneyUpdated: float = 0
