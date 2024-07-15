from pydantic import BaseModel


class AwardInfoDeprecated(BaseModel):
    awardId: int
    awardImg: str
    awardName: str
    awardDescription: str
    levelName: str
    color: str
    skinName: str | None
