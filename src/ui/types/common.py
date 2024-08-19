from pathlib import Path
from pydantic import BaseModel, computed_field


class LevelData(BaseModel):
    display_name: str
    color: str
    lid: int


class AwardInfo(BaseModel):
    aid: int
    description: str
    display_name: str
    color: str
    image_name: str
    image_type: str
    level: LevelData
    sorting: int

    @property
    def image_path(self) -> Path:
        return Path("./data") / self.image_type / self.image_name

    @computed_field
    @property
    def image_url(self) -> str:
        return f"../file/{self.image_type}/{self.image_name}"


class UserData(BaseModel):
    uid: int
    qqid: str
    name: str


class GetAward(BaseModel):
    info: AwardInfo
    count: int
    is_new: bool
