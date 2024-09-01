from pydantic import BaseModel

from src.ui.types.common import UserData


class DisplayBoxData(BaseModel):
    image: str
    color: str
    notation_up: str = ""
    notation_down: str = ""
    new_overlay: bool = False
    notation_up_color: str = "#FFFFFF"
    notation_down_color: str = "#FFFFFF"
    do_glow: bool = False
    glow_type: int = 0


class BookBoxData(BaseModel):
    display_box: DisplayBoxData
    title1: str
    title2: str = ""


class BoxItemList(BaseModel):
    title: str = ""
    "标题留空时不显示小标题"

    title_color: str = "#FFFFFF"
    elements: list[BookBoxData]


class StorageData(BaseModel):
    user: UserData
    boxes: list[BoxItemList] = []
    title_text: str = "小哥库存"
