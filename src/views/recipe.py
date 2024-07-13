from enum import Enum

from pydantic import BaseModel

from .award import AwardInfo


class MergeStatus(Enum):
    success = "成功！"
    fail = "失败！"
    what = "失败？"


class MergeResult(BaseModel):
    """
    合成小哥时的消息
    """

    username: str
    successed: MergeStatus
    inputs: tuple[AwardInfo, AwardInfo, AwardInfo]
    output: AwardInfo
    cost_money: int
    remain_money: int

    @property
    def title1(self):
        return f"{self.username} 的合成材料："

    @property
    def title2(self):
        return f"合成结果：{self.successed.value}"
    
    @property
    def title3(self):
        return f"本次合成花费了你 {self.cost_money} 薯片，你还有 {self.remain_money} 薯片。"
