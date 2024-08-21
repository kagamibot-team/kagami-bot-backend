from pydantic import BaseModel

from src.ui.types.common import AwardInfo, GetAward, UserData


class MergeMeta(BaseModel):
    cost_chip: int
    own_chip: int
    status: str
    is_strange: bool


class MergeData(BaseModel):
    user: UserData
    inputs: tuple[AwardInfo, AwardInfo, AwardInfo]
    output: GetAward
    meta: MergeMeta
