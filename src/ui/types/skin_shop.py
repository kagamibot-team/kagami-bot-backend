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


class SkinShopBought(BaseModel):
    user: UserData
    rest_money: int
    cost: int
    unit: str
    image: str | None = None
    name: str
    current_count: int | None = None
    from_award_name: str | None = None
    level: int | None = None


class SkinPackOpenBiscuitDelta(BaseModel):
    delta: int
    after: int


class SkinPackOpen(BaseModel):
    user: UserData
    biscuit_delta: None | SkinPackOpenBiscuitDelta
    image: str
    level: int
    dialog: DialogueMessage
    skin_name: str
    skin_award_name: str
