"""
猎场 UI 的数据
"""

from pathlib import Path
import PIL
import PIL.Image
from pydantic import BaseModel

from src.models.level import Level
from src.ui.views.award import AwardInfo
from src.ui.views.user import UserData


IMAGE_TEMP: dict[Path, PIL.Image.Image] = {}


def get_img(path: Path) -> PIL.Image.Image:
    if path not in IMAGE_TEMP:
        IMAGE_TEMP[path] = PIL.Image.open(path).convert("RGBA")
    return IMAGE_TEMP[path]


class SinglePackView(BaseModel):
    """
    玩家的其中一个猎场的视图
    """

    pack_id: int
    "猎场的 ID"

    award_count: list[tuple[Level, tuple[int, int]]]
    "各个等级，玩家收集了多少小哥，以及各有多少个小哥"

    featured_award: AwardInfo
    "这个猎场最特色的小哥，用于在界面中展示"

    unlocked: bool
    "用户解锁了这个猎场了么"

    selected: bool
    "用户正在选择这个猎场么"

    @property
    def background_path(self) -> Path:
        p1 = Path(f"./res/pack/背景 {self.pack_id}.png")
        if not p1.exists():
            return Path("./res/pack/背景 1.png")
        return p1

    @property
    def background(self) -> PIL.Image.Image:
        return get_img(self.background_path)

    @property
    def chatbox(self) -> PIL.Image.Image:
        return get_img(Path("./res/pack/chatbox.png"))


class PackView(BaseModel):
    """
    玩家的猎场的视图
    """

    packs: list[SinglePackView]
    "所有的猎场"

    user: UserData
    "用户的信息"
