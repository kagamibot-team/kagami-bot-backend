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
