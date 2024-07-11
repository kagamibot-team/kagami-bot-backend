from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..base.repository import BaseRepository
from ..models import Inventory


class InventoryRepository(BaseRepository[Inventory]):
    """
    和玩家的小哥库存和皮肤记录有关的仓库
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Inventory)

    async def assure(self, uid: int, aid: int):
        """确保数据库中有这个玩家对该小哥的记录，没有则创建

        Args:
            uid (int): 玩家的id
            aid (int): 小哥的id
        """
        query = select(Inventory.data_id).filter(
            Inventory.user_id == uid,
            Inventory.award_id == aid,
        )
        result = await self.session.execute(query)
        if not result.scalars().first():
            await self.add(Inventory(uid=uid, aid=aid))

    async def get_count(self, uid: int, aid: int) -> int:
        """获取玩家某个小哥的数量

        Args:
            uid (int): 玩家的id
            aid (int): 小哥的id

        Returns:
            int: 数量
        """
        await self.assure(uid, aid)
        query = select(Inventory.storage).filter(
            Inventory.user_id == uid,
            Inventory.award_id == aid,
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_stats(self, uid: int, aid: int) -> int:
        """获取玩家某个小哥的统计数据

        Args:
            uid (int): 玩家的id
            aid (int): 小哥的id

        Returns:
            int: 数量
        """
        await self.assure(uid, aid)
        query = select(Inventory.storage, Inventory.used).filter(
            Inventory.user_id == uid,
            Inventory.award_id == aid,
        )
        result = await self.session.execute(query)
        count, used = result.tuples().one()
        return count + used

    async def obtain(self, uid: int, aid: int, count: int):
        """获取小哥

        Args:
            uid (int): 玩家的id
            aid (int): 小哥的id
            count (int): 获取的数量
        """
        await self.assure(uid, aid)
        query = (
            update(Inventory)
            .where(
                Inventory.user_id == uid,
                Inventory.award_id == aid,
            )
            .values(count=Inventory.storage + count)
        )

        await self.session.execute(query)

    async def use(self, uid: int, aid: int, count: int):
        """消耗小哥，会减少库存，并记录使用数量

        Args:
            uid (int): 玩家的id
            aid (int): 小哥的id
            count (int): 使用的数量
        """
        await self.assure(uid, aid)
        query = (
            update(Inventory)
            .where(
                Inventory.user_id == uid,
                Inventory.award_id == aid,
            )
            .values(count=Inventory.storage - count, used=Inventory.used + count)
        )

        await self.session.execute(query)

    async def get_count_dict(self, uid: int) -> dict[int, int]:
        """获取玩家所有小哥库存的字典

        Args:
            uid (int): 玩家的id

        Returns:
            dict: 字典
        """
        query = select(Inventory.award_id, Inventory.storage).filter(Inventory.user_id == uid)
        result = await self.session.execute(query)
        return dict(result.tuples())
