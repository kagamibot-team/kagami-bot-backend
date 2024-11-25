from pydantic import BaseModel

from src.base.res import blank_placeholder
from src.ui.types.common import UserData


class DisplayBoxData(BaseModel):
    image: str
    color: str

    notation_up: str = ""
    notation_down: str = ""
    notation_up_color: str = "#FFFFFF"
    notation_down_color: str = "#FFFFFF"

    do_glow: bool = False
    glow_type: int = 0

    new_overlay: bool = False
    sold_out_overlay: bool = False
    black_overlay: bool = False


class BookBoxData(BaseModel):
    display_box: DisplayBoxData
    title1: str
    title2: str = ""

    @staticmethod
    def unknown():
        return BookBoxData(
            display_box=DisplayBoxData(
                image=blank_placeholder().url,
                color="#696361",
            ),
            title1="???",
        )


class BoxItemList(BaseModel):
    title: str = ""
    "标题留空时不显示小标题"

    title_color: str = "#FFFFFF"
    elements: list[BookBoxData]


class StorageData(BaseModel):
    user: UserData
    boxes: list[BoxItemList] = []
    title_text: str = "小哥库存"
