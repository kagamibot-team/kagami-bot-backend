from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.dataclasses.user import UserTime


class Pick(BaseModel):
    """
    单条抓小哥的记录
    """

    beforeStats: int
    delta: int
    level: int


class Picks(BaseModel):
    """
    一个记录抓小哥结果的数据类，仅储存在内存中，可以在后续流程中更改其中的结果。
    """

    awards: dict[int, Pick]
    money: float
    uid: int


class PicksEvent:
    """
    抓小哥事件，在抓小哥之后、库存数据写入数据库之前时触发的事件
    """

    uid: int
    group_id: int | None
    picks: Picks
    session: AsyncSession

    def __init__(
        self, uid: int, group_id: int | None, picks: Picks, session: AsyncSession
    ) -> None:
        self.uid = uid
        self.group_id = group_id
        self.picks = picks
        self.session = session


class PickDisplay(BaseModel):
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


class PrePickMessageEvent:
    """
    在抓小哥数据库存写入之后、关闭数据库并构建返回给用户的消息之前触发的事件
    """

    picks: Picks
    group_id: int | None
    displays: dict[int, PickDisplay]
    uid: int
    session: AsyncSession
    userTime: UserTime
    moneyUpdated: float = 0

    def __init__(
        self,
        picks: Picks,
        group_id: int | None,
        displays: dict[int, PickDisplay],
        uid: int,
        session: AsyncSession,
        userTime: UserTime,
        moneyUpdated: float = 0,
    ) -> None:
        self.picks = picks
        self.group_id = group_id
        self.displays = displays
        self.uid = uid
        self.session = session
        self.userTime = userTime
        self.moneyUpdated = moneyUpdated
