from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ProductData:
    """在各种商店中存储商品和价格的数据类。"""

    image: str
    title: str
    description: str
    price: float
    sold_out: bool
    alias: list[str]
    background_color: str


@dataclass
class ShopData:
    """记录一个商店的信息"""

    products: list[ProductData]


@dataclass
class ShopBuildingEvent:
    """正在构造一个商店的事件"""

    data: ShopData
    qqid: int
    uid: int
    session: AsyncSession


@dataclass
class ShopBuyEvent:
    """商店购买事件"""

    product: ProductData
    qqid: int
    uid: int
    session: AsyncSession
