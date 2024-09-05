from pydantic import BaseModel

from src.ui.types.common import UserData
from src.ui.types.inventory import BookBoxData


class Product(BaseModel):
    title: str
    price: int


class ProductGroup(BaseModel):
    group_name: str
    products: list[BookBoxData]


class BuyData(BaseModel):
    date: str
    time: str
    user: UserData
    remain_chips: int
    records: list[Product]


class ShopDisplay(BaseModel):
    user: UserData
    chips: int
    products: list[ProductGroup]
