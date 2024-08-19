from pydantic import BaseModel


class LevelData(BaseModel):
    display_name: str
    color: str
    lid: int


class AwardInfo(BaseModel):
    description: str
    display_name: str
    color: str
    image: str
    level: LevelData


class UserData(BaseModel):
    uid: int
    qqid: str
    name: str


class GetAward(BaseModel):
    info: AwardInfo
    count: int
    is_new: bool
