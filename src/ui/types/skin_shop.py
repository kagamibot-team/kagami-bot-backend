from pydantic import BaseModel

from src.ui.types.common import DialogueMessage, UserData


class SkinBook(BaseModel):
    image: str
    level: int
    name: str
    is_drawable: bool
    price: int
    do_user_have: bool


class SkinShop(BaseModel):
    user: UserData
    chips: int
    biscuits: int
    skins: list[SkinBook]
    skin_pack_price: int
    dialog: DialogueMessage
