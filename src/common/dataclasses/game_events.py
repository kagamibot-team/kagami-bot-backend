from pydantic import BaseModel

from src.ui.views.award import GotAwardDisplay
from src.ui.views.catch import CatchMesssage, CatchResultMessage
from src.ui.views.user import UserData


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

    catch_view: CatchMesssage

    @property
    def successed(self):
        return isinstance(self.catch_view, CatchResultMessage)
    
    @property
    def results(self) -> list[GotAwardDisplay]:
        if not isinstance(self.catch_view, CatchResultMessage):
            return []
        return self.catch_view.catchs
