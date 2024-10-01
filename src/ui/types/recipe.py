from pydantic import BaseModel
from datetime import datetime

from src.ui.types.common import AwardInfo, GetAward, UserData


class MergeMeta(BaseModel):
    user: UserData
    cost_chip: int
    own_chip: int
    status: str
    is_strange: bool


class MergeData(BaseModel):  # 传递给前端用的合成信息
    inputs: tuple[AwardInfo, AwardInfo, AwardInfo]
    after_storages: tuple[int, int, int, int]
    light_off: tuple[bool, bool, bool, bool]
    possibility: float
    output: GetAward
    recipe_id: int
    stat_id: int
    last_time: str = ""
    meta: MergeMeta = MergeMeta(
        user=UserData(
            uid=0,
            qqid="",
            name="",
        ),
        cost_chip=0,
        own_chip=0,
        status="",
        is_strange=False,
    )


class RecipeArchiveData(BaseModel):
    user: UserData
    recipes: list[MergeData]
    product: AwardInfo
    cost_chip: int
    own_chip: int
    good_enough: bool


class RecipeInfo(BaseModel):  # 一整条配方信息
    recipe_id: int
    stat_id: int = 0
    aid1: int
    aid2: int
    aid3: int
    possibility: float
    result: int
    created_at: datetime
    updated_at: datetime
