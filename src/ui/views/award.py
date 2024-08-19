from pydantic import BaseModel

from src.ui.types.common import AwardInfo


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
