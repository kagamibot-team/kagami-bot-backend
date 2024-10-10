import datetime
import hashlib
from enum import Enum
from pathlib import Path

import PIL
import PIL.Image
from loguru import logger
from nonebot import get_driver
from pydantic import BaseModel, computed_field

from src.common.times import now_datetime


class LevelData(BaseModel):
    display_name: str = "未知"
    color: str = "#9e9d95"
    lid: int = -1


class AwardInfo(BaseModel):
    aid: int = 0
    description: str = "未知小哥。"
    name: str = "？？？"
    color: str = "#696361"
    image_name: str = "blank_placeholder.png"
    image_type: str = ""
    level: LevelData = LevelData()
    sorting: int = 0
    skin_name: str = ""

    @property
    def image_path(self) -> Path:
        if self.image_name == "default.png":
            return Path("./res/default.png")
        if self.image_name == "blank_placeholder.png":
            return Path("./res/blank_placeholder.png")
        return Path("./data") / self.image_type / self.image_name

    @computed_field
    @property
    def image_url_raw(self) -> str:
        if self.image_name == "default.png":
            return "/kagami-res/default.png"
        if self.image_name == "blank_placeholder.png":
            return "/kagami-res/blank_placeholder.png"
        return f"/kagami/file/{self.image_type}/{self.image_name}"

    @computed_field
    @property
    def image_url(self) -> str:
        if self.image_name == "default.png":
            return "/kagami-res/default.png"
        if self.image_name == "blank_placeholder.png":
            return "/kagami-res/blank_placeholder.png"
        _target_hash = hashlib.md5(
            str(self.image_path).encode() + self.image_path.read_bytes()
        ).hexdigest()
        _target_path = Path("./data/temp/") / f"temp_{_target_hash}.png"
        if not _target_path.exists():
            logger.info(f"正在创建 {self.image_path} 的缩小文件")
            img = PIL.Image.open(self.image_path)
            img = img.resize((175, 140))
            img.save(_target_path)
        return f"/kagami/file/temp/temp_{_target_hash}.png"

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
