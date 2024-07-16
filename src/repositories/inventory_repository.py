from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..base.repository import DBRepository
from ..models import Inventory


class InventoryRepository(DBRepository[Inventory]):
    """
    和玩家的小哥库存有关的仓库
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Inventory)

    async def set_inventory(self, uid: int, aid: int, storage: int, used: int):
        """设置玩家的小哥库存

        Args:
            uid (int): 用户 ID
            aid (int): 小哥 ID
            storage (int): 库存数量
            used (int): 用过的数量
        """
        query = (
            update(Inventory)
            .where(Inventory.user_id == uid, Inventory.award_id == aid)
            .values(storage=storage, used=used)
            .returning(Inventory.data_id)
        )

        result = (await self.session.execute(query)).scalars().all()
        if len(result) > 1:
            # 可能是奇怪的数据库问题，这个时候删掉原先的数据然后更改
            await self.session.execute(
                delete(Inventory).where(
                    Inventory.user_id == uid, Inventory.award_id == aid
                )
            )
            result = ()

        if len(result) == 0:
            # 这时候没有库存，很有可能是更新失败的情景，我们创建一个新的行
            await self.session.execute(
                insert(Inventory).values(
                    storage=storage, used=used, user_id=uid, award_id=aid
                )
            )

    async def get_inventory(self, uid: int, aid: int) -> tuple[int, int]:
        """获得小哥物品栏的原始信息

        Args:
            uid (int): 用户的 ID
            aid (int): 小哥的 ID

        Returns:
            tuple[int, int]: 两项分别是库存中有多少小哥，目前用掉了多少小哥
        """

        query = select(Inventory.storage, Inventory.used).filter(
            Inventory.user_id == uid, Inventory.award_id == aid
        )

        return (await self.session.execute(query)).tuples().one_or_none() or (0, 0)

    async def get_storage(self, uid: int, aid: int) -> int:
        """获取玩家某个小哥的库存数量

        Args:
            uid (int): 玩家的id
            aid (int): 小哥的id

        Returns:
            int: 数量
        """
        return (await self.get_inventory(uid, aid))[0]

    async def get_stats(self, uid: int, aid: int) -> int:
        """获取玩家某个小哥的统计数据

        Args:
            uid (int): 玩家的id
            aid (int): 小哥的id

        Returns:
            int: 数量
        """
        return sum(await self.get_inventory(uid, aid))

    async def give(self, uid: int, aid: int, count: int, record_used: bool=True) -> tuple[int, int]:
        """获取小哥，返回更新后的库存量和使用量

        Args:
            uid (int): 玩家的id
            aid (int): 小哥的id
            count (int): 获取的数量
            record_used (bool): 是否记录小哥的使用，默认开启
        """
        sto, use = await self.get_inventory(uid, aid)
        if count < 0 and record_used:
            use += -count
        sto += count
        await self.set_inventory(uid, aid, sto, use)
        return sto, use

    async def get_inventory_dict(self, uid: int) -> dict[int, tuple[int, int]]:
        """获取玩家所有小哥物品栏的字典

        Args:
            uid (int): 玩家的id

        Returns:
            dict[int, tuple[int, int]]: 字典，值的两项分别是库存和用过的
        """
        query = select(Inventory.award_id, Inventory.storage, Inventory.used).filter(
            Inventory.user_id == uid
        )
        result = await self.session.execute(query)
        return {aid: (sto, use) for aid, sto, use in result.tuples().all()}