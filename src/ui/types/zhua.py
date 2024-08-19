from pydantic import BaseModel

from src.ui.types.common import GetAward, UserData


class ZhuaMeta(BaseModel):
    field_from: int
    get_chip: int
    own_chip: int
    remain_time: int
    max_time: int
    need_time: str


class ZhuaData(BaseModel):
    user: UserData
    meta: ZhuaMeta
    catchs: list[GetAward]
