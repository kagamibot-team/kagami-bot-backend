from pydantic import BaseModel


class DisplayBoxData(BaseModel):
    image: str
    color: str
    notation_up: str = ""
    notation_down: str = ""
    new_overlay: bool = False
    notation_up_color: str = "#FFFFFF"
    notation_down_color: str = "#FFFFFF"


class BookBoxData(BaseModel):
    display_box: DisplayBoxData
    title1: str
    title2: str = ""
