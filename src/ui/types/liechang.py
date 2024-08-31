from pydantic import BaseModel

from src.ui.types.common import AwardInfo, LevelData, UserData


class LiechangCountInfo(BaseModel):
    level: LevelData
    collected: int
    sum_up: int


class SingleLiechang(BaseModel):
    pack_id: int
    award_count: list[LiechangCountInfo]
    featured_award: AwardInfo
    unlocked: bool


class DialogueMessage(BaseModel):
    text: str
    speaker: str
    face: str


class LiechangData(BaseModel):
    packs: list[SingleLiechang]
    user: UserData
    selecting: int
    dialogue: DialogueMessage
    chips: int
