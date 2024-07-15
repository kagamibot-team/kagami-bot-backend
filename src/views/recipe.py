from enum import Enum

from pydantic import BaseModel

from src.views.user import UserData

from .award import AwardInfo


class MergeStatus(Enum):
    success = "成功！"
    fail = "失败！"
    what = "失败？"


class MergeResult(BaseModel):
    """
    合成小哥时的消息
    """

    user: UserData
    successed: MergeStatus
    inputs: tuple[AwardInfo, AwardInfo, AwardInfo]
    output: AwardInfo
    cost_money: int
    remain_money: int

    @property
    def title1(self):
        return f"{self.user.name} 的合成材料："

    @property
    def title2(self):
        return f"合成结果：{self.successed.value}"

    @property
    def title3(self):
        return f"本次合成花费了你 {self.cost_money} 薯片，你还有 {self.remain_money} 薯片。"


class MergeHistory(BaseModel):
    """
    合成小哥的历史记录
    """

    inputs: tuple[AwardInfo, AwardInfo, AwardInfo]
    "用于合成的小哥"

    output: AwardInfo
    "合成结果"

    found_person: UserData
    "发现这个配方的人"


class MergeHistoryList(BaseModel):
    """
    合成小哥的历史记录列表
    """

    history: list[MergeHistory]
    "合成小哥的历史记录"
