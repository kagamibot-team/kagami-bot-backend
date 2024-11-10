import datetime
from enum import Enum
from pathlib import Path

from nonebot import get_driver
from pydantic import BaseModel, computed_field

from src.base.res import KagamiResourceManagers
from src.base.res.resource import IResource
from src.common.times import now_datetime


class LevelData(BaseModel):
    display_name: str = "未知"
    color: str = "#9e9d95"
    lid: int = -1


class AwardInfo(BaseModel):
    aid: int = 0
    description: str = "未知小哥。"
    name: str = "？？？"

    sid: int | None = None
    slevel: int | None = None
    level: LevelData = LevelData()
    sorting: int = 0
    skin_name: str = ""
    _img_resource: IResource | None = None
    pid: int = -1  # 猎场 ID，目前仅在 zhuajd 中使用到了

    @computed_field
    @property
    def display_lid(self) -> int:
        """
        这个 LID 也是屎山的一部分。

        如果没有皮肤，则值落在 0 ~ 5 之间，代表小哥的六种等级

        如果有皮肤，则值落在 10 ~ 14 之间，代表皮肤的等级
        """

        if self.sid is not None and self.slevel is not None:
            return 10 + self.slevel
        return self.level.lid

    @computed_field
    @property
    def color(self) -> str:
        level_map = {
            0: "#9E9D95",
            1: "#C6C1BF",
            2: "#C0E8AE",
            3: "#BDDAF5",
            4: "#D4BCE3",
            5: "#F1DD95",
            10: "#E57D77",
            11: "#75C16D",
            12: "#6F93E7",
            13: "#996FE0",
            14: "#E8BD5A",
        }
        return level_map[self.display_lid]

    @property
    def image_name(self) -> str:
        if self.sid is not None:
            return f"sid_{self.sid}.png"
        return f"aid_{self.aid}.png"

    @property
    def image_resource(self) -> IResource:
        if self._img_resource is not None:
            return self._img_resource
        if self.aid <= 0:
            return KagamiResourceManagers.xiaoge("blank_placeholder.png")
        return KagamiResourceManagers.xiaoge(self.image_name)

    @property
    def image_resource_small(self) -> IResource:
        if self._img_resource is not None:
            return self._img_resource
        if self.aid <= 0:
            return KagamiResourceManagers.xiaoge_low("blank_placeholder.png")
        return KagamiResourceManagers.xiaoge_low(self.image_name)

    @property
    def image_path(self) -> Path:
        return self.image_resource.path

    @computed_field
    @property
    def image_url_raw(self) -> str:
        return self.image_resource.url

    @computed_field
    @property
    def image_url(self) -> str:
        return self.image_resource_small.url

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


class HuaOutStage(Enum):
    stage_1 = 1
    stage_2 = 2
    stage_3 = 3
    stage_4 = 4
    "放出“接收影像_i”，正在解第i题"
    stage_end = 5
    "解完了四题，没剧情了"


class HuaOutMessage(BaseModel):
    speaker: str
    msg_time: datetime.datetime
    content: str
    success: bool
    recalc: bool = True

    def to_string(self) -> str:
        # 【华】2024/10/04 17:38:04（已换算）
        # 「诶……好像不太对……？」
        _rec = "（已换算）" if self.recalc else ""
        _time = self.msg_time.strftime("%Y/%m/%d %H:%M:%S")
        return f"【{self.speaker}】{_time}{_rec}\n「{self.content}」"


def get_msg_cooldown() -> float:
    return 600.0 if get_driver().env != "dev" else 10.0


class GlobalFlags(BaseModel):
    activity_hua_out: bool = False
    stage: HuaOutStage = HuaOutStage.stage_1

    messages: list[HuaOutMessage] = []
    last_wrong_time: datetime.datetime | None = None

    def can_message_now(self, now_time: datetime.datetime | None = None) -> bool:
        if now_time is None:
            now_time = now_datetime()
        if self.last_wrong_time is None:
            return True
        return (now_time - self.last_wrong_time).total_seconds() > get_msg_cooldown()

    def send_message(
        self,
        speaker: str,
        content: str,
        msg_time: datetime.datetime | None = None,
        success: bool = True,
        recalc: bool = False,
    ):
        """
        储存一条消息
        """
        if msg_time is None:
            msg_time = now_datetime()
        obj = HuaOutMessage(
            speaker=speaker,
            content=content,
            msg_time=msg_time,
            success=success,
            recalc=recalc,
        )
        self.messages.append(obj)
        return obj

    def trigger_fail(self, now_time: datetime.datetime | None = None):
        if now_time is None:
            now_time = now_datetime()
        self.last_wrong_time = now_time


class DialogueMessage(BaseModel):
    text: str
    speaker: str
    face: str
    scene: set[str] | None = None

    def dump_str(self):
        leading = ""
        if self.scene is not None:
            leading = ",".join(self.scene)
        return f"{leading}{self.speaker} {self.face}：{self.text}"
