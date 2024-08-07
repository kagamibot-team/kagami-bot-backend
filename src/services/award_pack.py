from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random
from typing import Iterable

from src.core.unit_of_work import UnitOfWork


@dataclass
class Source:
    """
    卡池的卡池源
    """

    weigth: float


class Sources:
    base = Source(1)
    special = Source(1.2)
    never = Source(0)


class AwardPack(ABC):
    """
    小哥卡池。
    """

    source: Source
    """
    这个机制比较复杂，主要是这样：

    - 首先计算一个用户当前挂载的所有卡池的 source_id
    - 然后从所有可用的 source_id 中抽一个
    - 接着计算该 source_id 所包含的等级，从等级中根据权重抽取
    - 最后在那个等级中抽取当前 source_id 中所有包含的小哥
    """

    def __init__(self, source: Source) -> None:
        self.source = source

    @abstractmethod
    async def get_all_id(self, uow: UnitOfWork) -> set[int]:
        """
        获得这个卡池下所有的小哥的 ID
        """

    async def contain_level(self, uow: UnitOfWork, lid: int) -> bool:
        return lid in await uow.awards.group_by_level(await self.get_all_id(uow))

    @abstractmethod
    async def check_using(self, uow: UnitOfWork, uid: int) -> bool:
        """
        检查一个用户现在有没有挂载这个卡池
        """


class NamedAwardPack(AwardPack, ABC):
    """
    一般是在商店中购买的那种卡池包
    """

    pack_id: str
    "在数据库中标注一个小哥属于哪一个卡池的识别 ID"

    def __init__(self, pack_id: str, source: Source) -> None:
        self.pack_id = pack_id
        super().__init__(source)

    async def get_all_id(self, uow: UnitOfWork) -> set[int]:
        return await uow.awards.get_all_awards_in_pack(self.pack_id)

    async def check_using(self, uow: UnitOfWork, uid: int) -> bool:
        return await uow.users.hanging_pack(uid) == self.pack_id


class DefaultAwardPack(AwardPack):
    """
    默认的小哥卡池
    """

    def __init__(self) -> None:
        super().__init__(source=Sources.base)

    async def get_all_id(self, uow: UnitOfWork) -> set[int]:
        return await uow.awards.get_all_default_awards()

    async def check_using(self, uow: UnitOfWork, uid: int) -> bool:
        return True


def get_sources(packs: Iterable[AwardPack]) -> list[Source]:
    """
    获得一系列卡池所包含的所有卡池源的集合
    """

    sources: list[Source] = []

    for pack in packs:
        sources.append(pack.source)

    return sources


async def get_aid_set(uow: UnitOfWork, packs: Iterable[AwardPack]) -> set[int]:
    """
    获得一系列卡池所包含的所有小哥
    """

    aids: set[int] = set()
    for pack in packs:
        aids |= await pack.get_all_id(uow)
    return aids


class AwardPackService:
    """
    用于维护一个小镜应用内的所有卡池
    """

    packs: list[AwardPack]

    def __init__(self) -> None:
        self.packs = []

    def register(self, pack: AwardPack):
        self.packs.append(pack)

    async def get_all_available_pack(self, uow: UnitOfWork, uid: int) -> set[AwardPack]:
        all_packs: set[AwardPack] = set()

        for pack in self.packs:
            if await pack.check_using(uow, uid):
                all_packs.add(pack)

        return all_packs

    async def random_choose_source(
        self,
        uow: UnitOfWork,
        uid: int,
        random: Random = Random(),
        lid: int | None = None,
    ) -> set[int]:
        """选择到随机一个池子"""

        all_packs = list(await self.get_all_available_pack(uow, uid))

        if lid is not None:
            all_packs = [
                pack for pack in all_packs if await pack.contain_level(uow, lid)
            ]

        sources = list(get_sources(all_packs))
        weights = [s.weigth for s in sources]

        source = random.choices(sources, weights)[0]
        packs = [pack for pack in all_packs if pack.source == source]

        return await get_aid_set(uow, packs)


def get_award_pack_service() -> AwardPackService:
    """获得一个小哥卡池的服务"""

    service = AwardPackService()

    service.register(DefaultAwardPack())

    return service
