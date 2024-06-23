from pydantic import BaseModel


class AwardInfo(BaseModel):
    awardId: int
    awardImg: str
    awardName: str
    awardDescription: str
    levelName: str
    color: str
    skinName: str | None