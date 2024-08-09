from pathlib import Path

from pydantic import BaseModel

from src.models.level import Level


class AwardInfo(BaseModel):
    aid: int
    name: str
    description: str
    level: Level
    image: Path | str | bytes
    sid: int | None = None
    skin_name: str | None = None
    sorting: int = 0
    pack_id: int = 1

    @property
    def color(self):
        return self.level.color

    @property
    def display_name(self):
        if self.skin_name is not None:
            return f"{self.name}[{self.skin_name}]"
        return self.name

    @property
    def image_path(self):
        assert isinstance(self.image, (str, Path))
        return Path(self.image)

    @property
    def image_bytes(self) -> bytes:
        if isinstance(self.image, (str, Path)):
            return Path(self.image).read_bytes()
        return self.image


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
