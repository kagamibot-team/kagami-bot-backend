from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.base.exceptions import ObjectNotFoundException
from src.base.res import KagamiResourceManagers
from src.base.res.resource import IResource
from src.core.unit_of_work import UnitOfWork
from src.repositories.skin_repository import SkinData
from src.ui.types.common import AwardInfo


@dataclass
class ShopProductFreezed:
    title: str
    description: str
    background_color: str
    image: IResource
    price: float
    is_sold_out: bool
    type: str


ShopFreezed = dict[str, list[ShopProductFreezed]]


class ShopProduct(ABC):
    """
    各种商店的商品的元类
    """

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
    async def image(self, uow: UnitOfWork, uid: int) -> IResource:
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

    async def title(self, uow: UnitOfWork, uid: int):
        return "皮肤" + self.info.name

    async def image(self, uow: UnitOfWork, uid: int):
        return KagamiResourceManagers.xiaoge_blurred(f"sid_{self.info.sid}.png")

    async def description(self, uow: UnitOfWork, uid: int):
        return f"{self.award.name}的皮肤"

    async def background_color(self, uow: UnitOfWork, uid: int):
        return self.award.color

    async def price(self, uow: UnitOfWork, uid: int):
        return self.info.deprecated_price

    async def is_sold_out(self, uow: UnitOfWork, uid: int) -> bool:
        return await uow.skin_inventory.do_user_have(uid, self.info.sid)

    def match(self, name: str) -> bool:
        return name in (self.info.name, "皮肤" + self.info.name)

    async def gain(self, uow: UnitOfWork, uid: int):
        await uow.skin_inventory.give(uid, self.info.sid)

    def __init__(self, award: AwardInfo, info: SkinData) -> None:
        self.info = info
        self.award = self.info.link(award)


class AddSlots(ShopProduct):
    @property
    def type(self):
        return "道具"

    async def _slots(self, uow: UnitOfWork, uid: int) -> int:
        return (await uow.user_catch_time.get_user_time(uid)).slot_count

    async def title(self, uow: UnitOfWork, uid: int):
        return "增加卡槽上限"

    async def description(self, uow: UnitOfWork, uid: int) -> str:
        return f"增加卡槽上限至{await self._slots(uow, uid) + 1}"

    async def image(self, uow: UnitOfWork, uid: int):
        return KagamiResourceManagers.res("add1.png")

    async def price(self, uow: UnitOfWork, uid: int) -> float:
        return 25 * (2 ** (await self._slots(uow, uid)))

    async def is_sold_out(self, uow: UnitOfWork, uid: int) -> bool:
        return False

    async def background_color(self, uow: UnitOfWork, uid: int):
        return "#97DD80"

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
        return "#9E9D95"

    async def price(self, uow: UnitOfWork, uid: int):
        return 1200

    async def image(self, uow: UnitOfWork, uid: int):
        return KagamiResourceManagers.res("merge_machine.png")

    async def is_sold_out(self, uow: UnitOfWork, uid: int) -> bool:
        return await uow.user_flag.have(uid, "合成")

    def match(self, name: str) -> bool:
        return name in ["小哥合成凭证", "合成小哥凭证", "合成凭证", "合成"]

    async def gain(self, uow: UnitOfWork, uid: int):
        await uow.user_flag.add(uid, "合成")


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
            raise ObjectNotFoundException("商品")
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
    for sid in await uow.skins.all_sid():
        sinfo = await uow.skins.get_info_v2(sid)
        ainfo = await uow.awards.get_info(sinfo.aid)
        if sinfo.deprecated_price <= 0:
            continue
        service.register(SkinProduct(ainfo, sinfo))

    return service
