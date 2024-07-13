from pathlib import Path

from pydantic import BaseModel

from src.models.statics import Level


class AwardInfo(BaseModel):
    aid: int
    name: str
    description: str
    level: Level
    image: Path | str | bytes

    sid: int | None
    skin_name: str | None

    new: bool
    notation: str

    @property
    def display_name(self):
        if self.skin_name is not None:
            return f"{self.name}[{self.skin_name}]"
        return self.name
