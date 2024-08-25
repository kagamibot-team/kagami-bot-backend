from pathlib import Path
from pydantic import BaseModel, computed_field


class LevelData(BaseModel):
    display_name: str
    color: str
    lid: int


class AwardInfo(BaseModel):
    aid: int
    description: str
    name: str
    color: str
    image_name: str
    image_type: str
    level: LevelData
    sorting: int
    skin_name: str = ""

    @property
    def image_path(self) -> Path:
        if self.image_name == "default.png":
            return Path("./res/default.png")
        return Path("./data") / self.image_type / self.image_name

    @computed_field
    @property
    def image_url(self) -> str:
        if self.image_name == "default.png":
            return "/kagami-res/default.png"
        return f"../file/{self.image_type}/{self.image_name}"

    @computed_field
    @property
    def display_name(self) -> str:
        if self.skin_name != "":
            return f"{self.name}[{self.skin_name}]"
        return self.name


class UserData(BaseModel):
    uid: int
    qqid: str
    name: str


class GetAward(BaseModel):
    info: AwardInfo
    count: int
    is_new: bool
