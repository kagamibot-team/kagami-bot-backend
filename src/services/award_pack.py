from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random
from typing import Iterable

from src.core.unit_of_work import UnitOfWork
from src.models.level import Level


@dataclass
class Source:
    """
    卡池的卡池源
    """

    name: str
    weigth: float

    def __hash__(self) -> int:
        return hash((self.name, self.weigth))


BASE_SOURCE = Source("默认", 1)
SPECIAL_SOURCE = Source("up池", 1.5)


class AwardPack(ABC):
    """
    小哥卡池。

    卡池的机制比较复杂，主要是这样：

    - 首先先抽一个等级
    - 然后看看这些等级有哪些小哥源
    - 从可以用的小哥源中，根据权重抽取一个
    - 最后抽取这个小哥源中符合该等级的全部小哥
    """

    @abstractmethod
    async def get_source_and_ids(self, uow: UnitOfWork) -> dict[Source, set[int]]:
        """
        获得这个卡池下所有的源以及对应的 ID
        """

    @abstractmethod
    async def do_available_for_user(self, uow: UnitOfWork, uid: int) -> bool:
        """
        检查一个卡池是否为激活状态
        """

    async def get_all_ids(self, uow: UnitOfWork) -> set[int]:
        ids: set[int] = set()

        for vals in (await self.get_source_and_ids(uow)).values():
            for val in vals:
                ids.add(val)

        return ids

    async def contain_level(self, uow: UnitOfWork, lid: int) -> bool:
        return lid in await uow.awards.group_by_level(await self.get_all_ids(uow))


class NamedAwardPack(AwardPack):
    """
    可以由用户切换的卡池包
    """

    pack_id: str
    "在数据库中标注一个小哥属于哪一个卡池的识别 ID"

    def __init__(self, pack_id: str) -> None:
        self.pack_id = pack_id

    async def get_source_and_ids(self, uow: UnitOfWork) -> dict[Source, set[int]]:
        aids_all = await uow.awards.get_all_awards_in_pack(self.pack_id)
        grouped = await uow.awards.group_by_level(aids_all)

        results: dict[Source, set[int]] = {
            BASE_SOURCE: set(),
            SPECIAL_SOURCE: set(),
        }

        for lid, aids in grouped.items():
            key = SPECIAL_SOURCE if lid >= 4 else BASE_SOURCE
            results[key] |= aids

        return results

    async def do_available_for_user(self, uow: UnitOfWork, uid: int) -> bool:
        return await uow.users.hanging_pack(uid) == self.pack_id


class DefaultAwardPack(AwardPack):
    """
    默认的小哥卡池
    """

    async def get_source_and_ids(self, uow: UnitOfWork) -> dict[Source, set[int]]:
        return {BASE_SOURCE: await uow.awards.get_all_default_awards()}

    async def do_available_for_user(self, uow: UnitOfWork, uid: int) -> bool:
        return True


async def get_sources(uow: UnitOfWork, packs: Iterable[AwardPack]) -> set[Source]:
    """
    获得一系列卡池所包含的所有卡池源的集合
    """

    sources: set[Source] = set()

    for pack in packs:
        mapping = await pack.get_source_and_ids(uow)
        mapping_keys = {key for key in mapping if len(mapping[key]) > 0}
        sources |= mapping_keys

    return sources


class AwardPackService:
    """
    用于维护一个小镜应用内的所有卡池
    """

    packs: list[AwardPack]

    def __init__(self) -> None:
        self.packs = []

    def register(self, pack: AwardPack):
        self.packs.append(pack)

    def exist_name(self, pack_name: str):
        for pack in self.packs:
            if isinstance(pack, NamedAwardPack):
                if pack_name == pack.pack_id:
                    return True

        return False

    async def get_all_available_pack(self, uow: UnitOfWork, uid: int) -> set[AwardPack]:
        """
        获得一个用户当前使用的所有的包
        """
        all_packs: set[AwardPack] = set()

        for pack in self.packs:
            if await pack.do_available_for_user(uow, uid):
                all_packs.add(pack)

        return all_packs

    async def get_all_aids(self, uow: UnitOfWork, uid: int) -> set[int]:
        """
        获得一个用户当前卡池的所有小哥
        """

        result: set[int] = set()

        for pack in await self.get_all_available_pack(uow, uid):
            result |= await pack.get_all_ids(uow)

        return result

    async def get_all_available_levels(self, uow: UnitOfWork, uid: int) -> list[Level]:
        """
        获得一个用户目前含有的包中所包含的全部等级
        """

        mappings = await uow.awards.group_by_level(await self.get_all_aids(uow, uid))
        levels = [uow.levels.get_by_id(lid) for lid in mappings]

        return levels

    async def random_choose_source(
        self,
        uow: UnitOfWork,
        uid: int,
        random: Random = Random(),
        lid: int | None = None,
    ) -> set[int]:
        """根据等级选择到随机一个池子"""

        # 获取所有可用的池子
        all_packs = list(await self.get_all_available_pack(uow, uid))
        # 如果指定了等级，则过滤出包含该等级的池子
        if lid is not None:
            all_packs = [
                pack for pack in all_packs if await pack.contain_level(uow, lid)
            ]
        # 遍历所有池子，获取每个池子的来源和对应的id
        mappings: dict[Source, set[int]] = {}
        for pack in all_packs:
            _mappings = await pack.get_source_and_ids(uow)
            for source, aids in _mappings.items():
                # 如果该来源有小哥，则添加到字典中
                if len(aids) > 0:
                    mappings.setdefault(source, set())
                    mappings[source] |= aids
        # 获取所有来源
        sources = list(mappings.keys())
        # 计算每个来源的权重
        weights = [s.weigth for s in sources]
        # 根据权重随机选择一个来源
        source = random.choices(sources, weights)[0]

        # 获取该来源的所有小哥
        aids = mappings[source]

        # 如果指定了等级，则过滤出该等级的所有小哥
        if lid is not None:
            aids = (await uow.awards.group_by_level(aids))[lid]

        return aids


def get_award_pack_service() -> AwardPackService:
    """获得一个小哥卡池的服务"""

    service = AwardPackService()

    service.register(DefaultAwardPack())
    service.register(NamedAwardPack("猎场：小秘封活动记录"))

    return service
