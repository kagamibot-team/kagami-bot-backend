from pydantic import BaseModel

from src.ui.types.common import UserData


class Product(BaseModel):
    title: str
    price: int


class BuyData(BaseModel):
    date: str
    time: str
    user: UserData
    remain_chips: int
    records: list[Product]
