from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class ProductData(BaseModel):
    """在各种商店中存储商品和价格的数据类。"""

    image: str
    title: str
    description: str
    price: float
    sold_out: bool
    alias: list[str]
    background_color: str


class ShopData(BaseModel):
    """记录一个商店的信息"""

    products: dict[str, list[ProductData]] = {}

    def push(self, product: ProductData, ptype: str):
        """将商品添加到商店中。"""
        self.products.setdefault(ptype, []).append(product)

    def iterate(self):
        """迭代商店中的商品。"""
        for product_list in self.products.values():
            yield from product_list


class ShopBuildingEvent:
    """正在构造一个商店的事件"""

    data: ShopData
    qqid: int
    uid: int
    session: AsyncSession

    def __init__(
        self, data: ShopData, qqid: int, uid: int, session: AsyncSession
    ) -> None:
        self.data = data
        self.qqid = qqid
        self.uid = uid
        self.session = session


class ShopBuyEvent:
    """商店购买事件"""

    product: ProductData
    qqid: int
    uid: int
    session: AsyncSession

    def __init__(
        self, product: ProductData, qqid: int, uid: int, session: AsyncSession
    ) -> None:
        self.product = product
        self.qqid = qqid
        self.uid = uid
        self.session = session
