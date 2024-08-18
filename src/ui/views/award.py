from pathlib import Path

import PIL
import PIL.Image
from pydantic import BaseModel

from src.models.level import Level


IMAGE_TEMP: dict[Path, PIL.Image.Image] = {}


class AwardInfo(BaseModel):
    """
    小哥的基础信息
    """

    aid: int
    name: str
    award_description: str
    award_image: str

    level: Level

    sorting: int = 0
    pack_id: int = 1

    sid: int | None = None
    skin_name: str | None = None
    skin_image: str | None = None
    skin_description: str | None = None

    @property
    def color(self):
        return self.level.color

    @property
    def display_name(self):
        if self.skin_name is not None:
            return f"{self.name}[{self.skin_name}]"
        return self.name

    @property
    def image(self) -> PIL.Image.Image:
        p = self.image_path
        if p not in IMAGE_TEMP:
            IMAGE_TEMP[p] = PIL.Image.open(p).convert("RGBA")
        return IMAGE_TEMP[p]

    @property
    def image_bytes(self) -> bytes:
        return self.image_path.read_bytes()

    @property
    def image_path(self) -> Path:
        if self.skin_image is None:
            return Path("./data/awards") / self.award_image
        return Path("./data/skins") / self.skin_image

    @property
    def image_url(self) -> str:
        if self.skin_image is None:
            return "../file/award/" + self.award_image
        return "../file/skin/" + self.skin_image

    @property
    def description(self) -> str:
        if self.skin_description is None:
            return self.award_description
        return self.skin_description


class LevelView(BaseModel):
    display_name: str
    color: str
    lid: int

    @staticmethod
    def from_model(lv: Level) -> "LevelView":
        return LevelView(
            display_name=lv.display_name,
            color=lv.color,
            lid=lv.lid,
        )


class InfoView(BaseModel):
    description: str
    display_name: str
    color: str
    image: str
    level: LevelView

    @staticmethod
    def from_award_info(info: AwardInfo) -> "InfoView":
        return InfoView(
            description=info.description,
            display_name=info.name,
            color=info.color,
            image=info.image_url,
            level=LevelView.from_model(info.level),
        )


class AwardDisplay(BaseModel):
    info: AwardInfo

    @property
    def notation(self) -> str:
        return ""

    @property
    def notation2(self) -> str:
        return ""

    @property
    def name_notation(self) -> str:
        return ""

    @property
    def new(self) -> bool:
        return False

    @property
    def sold_out(self) -> bool:
        return False


class DisplayData(BaseModel):
    info: InfoView
    count: int | None = None


class GotAwardDisplay(AwardDisplay):
    count: int
    is_new: bool

    @property
    def notation(self):
        return f"+{self.count}"

    @property
    def new(self):
        return self.is_new


class StorageDisplay(AwardDisplay):
    do_show_notation1: bool = True
    do_show_notation2: bool = False

    storage: int
    stats: int

    @property
    def notation(self):
        return str(self.storage) if self.do_show_notation1 else ""

    @property
    def notation2(self):
        return str(self.stats) if self.do_show_notation2 else ""
