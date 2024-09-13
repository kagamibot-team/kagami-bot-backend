from pydantic import BaseModel
from datetime import datetime

from src.ui.types.common import AwardInfo, GetAward, UserData


class MergeMeta(BaseModel):
    recipe_id: int
    stat_id: int
    cost_chip: int
    own_chip: int
    status: str
    is_strange: bool


class MergeData(BaseModel): # 传递给前端用
    user: UserData
    inputs: tuple[AwardInfo, AwardInfo, AwardInfo]
    output: GetAward
    meta: MergeMeta


class RecipeInfo(BaseModel): # 一整条配方信息
    aid1: int
    aid2: int
    aid3: int
    possibility: float
    result: int
    created_at: datetime
    updated_at: datetime