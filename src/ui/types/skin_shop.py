from pydantic import BaseModel

from src.repositories.skin_repository import SkinData
from src.ui.types.common import UserData


class SkinBook(BaseModel):
    info: SkinData
    do_user_have: bool


class SkinShop(BaseModel):
    user: UserData
    chips: int
    biscuits: int
    skins: list[SkinBook]
    skin_pack_price: int
