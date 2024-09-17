import hashlib
from pathlib import Path

import PIL
import PIL.Image
from loguru import logger
from pydantic import BaseModel, computed_field


class LevelData(BaseModel):
    display_name: str = "未知"
    color: str = "#9e9d95"
    lid: int = -1


class AwardInfo(BaseModel):
    aid: int = 0
    description: str = "未知小哥。"
    name: str = "？？？"
    color: str = "#696361"
    image_name: str = "blank_placeholder.png"
    image_type: str = ""
    level: LevelData = LevelData()
    sorting: int = 0
    skin_name: str = ""

    @property
    def image_path(self) -> Path:
        if self.image_name == "default.png":
            return Path("./res/default.png")
        if self.image_name == "blank_placeholder.png":
            return Path("./res/blank_placeholder.png")
        return Path("./data") / self.image_type / self.image_name

    @computed_field
    @property
    def image_url_raw(self) -> str:
        if self.image_name == "default.png":
            return "/kagami-res/default.png"
        if self.image_name == "blank_placeholder.png":
            return "/kagami-res/blank_placeholder.png"
        return f"/kagami/file/{self.image_type}/{self.image_name}"

    @computed_field
    @property
    def image_url(self) -> str:
        if self.image_name == "default.png":
            return "/kagami-res/default.png"
        if self.image_name == "blank_placeholder.png":
            return "/kagami-res/blank_placeholder.png"
        _target_hash = hashlib.md5(
            str(self.image_path).encode() + self.image_path.read_bytes()
        ).hexdigest()
        _target_path = Path("./data/temp/") / f"temp_{_target_hash}.png"
        if not _target_path.exists():
            logger.info(f"正在创建 {self.image_path} 的缩小文件")
            img = PIL.Image.open(self.image_path)
            img = img.resize((175, 140))
            img.save(_target_path)
        return f"/kagami/file/temp/temp_{_target_hash}.png"

    @computed_field
    @property
    def display_name(self) -> str:
        if self.skin_name != "":
            return f"{self.name}[{self.skin_name}]"
        return self.name


class UserData(BaseModel):
    uid: int = -1
    qqid: str = ""
    name: str = "管理员"


class GetAward(BaseModel):
    info: AwardInfo
    count: int
    is_new: bool


class DisplayAward(GetAward):
    stats: str = ""
