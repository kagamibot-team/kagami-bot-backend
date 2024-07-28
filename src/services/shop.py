from abc import ABC, abstractmethod
from pathlib import Path

import PIL
import PIL.Image
import PIL.ImageFilter
from pydantic import BaseModel

from src.base.exceptions import ObjectNotFoundException
from src.core.unit_of_work import UnitOfWork


class ShopProductFreezed(BaseModel):
    title: str
    description: str
    background_color: str
    image: Path
    price: float
    is_sold_out: bool
    type: str


ShopFreezed = dict[str, list[ShopProductFreezed]]


class ShopProduct(ABC):
    @abstractmethod
    async def title(self, uow: UnitOfWork, uid: int) -> str:
        """商品的标题"""

    @abstractmethod
    async def description(self, uow: UnitOfWork, uid: int) -> str:
        """商品的描述"""

    @abstractmethod
    async def background_color(self, uow: UnitOfWork, uid: int) -> str:
        """商品的背景颜色"""

    @abstractmethod
    async def price(self, uow: UnitOfWork, uid: int) -> float:
        """商品的价格"""

    @abstractmethod
    async def is_sold_out(self, uow: UnitOfWork, uid: int) -> bool:
        """判断一个商品是否被卖光"""

    @abstractmethod
    def match(self, name: str) -> bool:
        """判断用户输入的名字是否符合这个产品"""

    @abstractmethod
    async def gain(self, uow: UnitOfWork, uid: int):
        """成功购买一个商品时触发的操作"""

    @abstractmethod
    async def image(self, uow: UnitOfWork, uid: int) -> Path:
        """商品的图片"""

    @property
    @abstractmethod
    def type(self) -> str:
        """商品的类型"""

    async def freeze(self, uow: UnitOfWork, uid: int) -> ShopProductFreezed:
        return ShopProductFreezed(
            title=await self.title(uow, uid),
            description=await self.description(uow, uid),
            background_color=await self.background_color(uow, uid),
            image=await self.image(uow, uid),
            price=await self.price(uow, uid),
            is_sold_out=await self.is_sold_out(uow, uid),
            type=self.type,
        )


class SkinProduct(ShopProduct):
    @property
    def type(self):
        return "皮肤"

    @property
    def cache(self) -> Path:
        return Path("./data/temp") / (
            "blurred_" + hex(hash(Path(self._image).read_bytes()))[2:] + ".png"
        )

    async def title(self, uow: UnitOfWork, uid: int):
        return "皮肤" + self._title

    async def image(self, uow: UnitOfWork, uid: int):
        if not self.cache.exists():
            raw = PIL.Image.open(self._image)
            raw = raw.filter(PIL.ImageFilter.BoxBlur(100))
            raw.save(self.cache)
        return self.cache

    async def description(self, uow: UnitOfWork, uid: int):
        return f"{self._aname}的皮肤"

    async def background_color(self, uow: UnitOfWork, uid: int):
        return self._bgc

    async def price(self, uow: UnitOfWork, uid: int):
        return self._price

    async def is_sold_out(self, uow: UnitOfWork, uid: int) -> bool:
        return await uow.skin_inventory.do_user_have(uid, self.sid)

    def match(self, name: str) -> bool:
        return name in (self._title, "皮肤" + self._title)

    async def gain(self, uow: UnitOfWork, uid: int):
        await uow.skin_inventory.give(uid, self.sid)

    def __init__(
        self, sid: int, name: str, image: str, aname: str, price: float, bgc: str
    ) -> None:
        self.sid = sid
        self._title = name
        self._image = image
        self._aname = aname
        self._bgc = bgc
        self._price = price


class AddSlots(ShopProduct):
    @property
    def type(self):
        return "道具"

    async def _slots(self, uow: UnitOfWork, uid: int):
        return (await uow.users.get_catch_time_data(uid))[0]

    async def title(self, uow: UnitOfWork, uid: int):
        return "增加卡槽上限"

    async def description(self, uow: UnitOfWork, uid: int) -> str:
        return f"增加卡槽上限至{await self._slots(uow, uid)}"

    async def image(self, uow: UnitOfWork, uid: int):
        return Path("./res/add1.png")

    async def price(self, uow: UnitOfWork, uid: int) -> float:
        return 25 * (2 ** ((await self._slots(uow, uid)) - 1))

    async def is_sold_out(self, uow: UnitOfWork, uid: int) -> bool:
        return False

    async def background_color(self, uow: UnitOfWork, uid: int):
        return "#9e9d95"

    def match(self, name: str) -> bool:
        return name in ["加上限", "增加上限", "增加卡槽上限"]

    async def gain(self, uow: UnitOfWork, uid: int):
        await uow.users.add_slot_count(uid, 1)


class MergeMachine(ShopProduct):
    @property
    def type(self):
        return "道具"

    async def title(self, uow: UnitOfWork, uid: int):
        return "小哥合成凭证"

    async def description(self, uow: UnitOfWork, uid: int):
        return "购买合成小哥机器的使用权"

    async def background_color(self, uow: UnitOfWork, uid: int):
        return "#9e9d95"

    async def price(self, uow: UnitOfWork, uid: int):
        return 1200

    async def image(self, uow: UnitOfWork, uid: int):
        return Path("./res/merge_machine.png")

    async def is_sold_out(self, uow: UnitOfWork, uid: int) -> bool:
        return await uow.users.do_have_flag(uid, "合成")

    def match(self, name: str) -> bool:
        return name in ["小哥合成凭证", "合成小哥凭证", "合成凭证", "合成"]

    async def gain(self, uow: UnitOfWork, uid: int):
        await uow.users.add_flag(uid, "合成")


class ShopService:
    products: dict[str, list[ShopProduct]]

    def __init__(self) -> None:
        self.products = {}

    def register(self, product: ShopProduct):
        self.products.setdefault(product.type, [])
        self.products[product.type].append(product)

    def get(self, name: str) -> ShopProduct | None:
        for ls in self.products.values():
            for p in ls:
                if p.match(name):
                    return p

        return None

    def __getitem__(self, name: str) -> ShopProduct:
        p = self.get(name)
        if p is None:
            raise ObjectNotFoundException("商品", name)
        return p

    async def freeze(self, uow: UnitOfWork, uid: int) -> ShopFreezed:
        result: ShopFreezed = {}
        for key, items in self.products.items():
            result[key] = [await i.freeze(uow, uid) for i in items]
        return result


async def build_xjshop(uow: UnitOfWork) -> ShopService:
    service = ShopService()

    # 注册道具
    service.register(MergeMachine())
    service.register(AddSlots())

    # 注册皮肤信息
    for sid, aid, sname, _, simage, price in await uow.skins.all():
        if price <= 0:
            continue
        aname, _, lid, _ = await uow.awards.get_info(aid)
        level = uow.levels.get_by_id(lid)
        service.register(SkinProduct(sid, sname, simage, aname, price, level.color))

    return service
