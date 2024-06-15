from dataclasses import dataclass


@dataclass
class AwardInfo:
    awardId: int
    awardImg: str
    awardName: str
    awardDescription: str
    levelName: str
    color: str
    skinName: str | None