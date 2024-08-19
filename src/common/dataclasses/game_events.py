from pydantic import BaseModel

from src.ui.types.recipe import MergeData
from src.ui.types.zhua import GetAward, ZhuaData
from src.ui.types.common import UserData


class UserDataUpdatedEvent(BaseModel):
    """
    在需要刷新游戏数据时传递的事件，目前只用于激活成就判定
    """

    user_data: UserData

    @property
    def uid(self):
        return self.user_data.uid


class DummyEvent(UserDataUpdatedEvent):
    """
    用于试验 / 特殊情况的事件，此时使用字符串传参
    """

    data: str


class UserTryCatchEvent(UserDataUpdatedEvent):
    """
    抓小哥时触发的事件
    """

    data: ZhuaData

    @property
    def successed(self) -> bool:
        return len(self.data.catchs) > 0

    @property
    def results(self) -> list[GetAward]:
        return self.data.catchs


class MergeEvent(UserDataUpdatedEvent):
    """
    合成小哥的时候触发的事件
    """

    merge_view: MergeData
