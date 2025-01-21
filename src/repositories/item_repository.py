from sqlalchemy import insert, select, update

from src.base.exceptions import LackException
from src.base.repository import DBRepository
from src.models.item import ItemInventory


class ItemRepository(DBRepository):
    async def assure(self, uid: int, item_id: str) -> None:
        """
        保证数据库中存在相应字段
        """
        q = select(ItemInventory.data_id).filter(
            ItemInventory.uid == uid, ItemInventory.item_id == item_id
        )
        r = await self.session.execute(q)
        re = r.scalar_one_or_none()
        if re is None:
            q = insert(ItemInventory).values(
                {
                    ItemInventory.uid: uid,
                    ItemInventory.item_id: item_id,
                }
            )
            await self.session.execute(q)
            await self.session.flush()

    async def set(
        self,
        uid: int,
        item_id: str,
        count: int | None = None,
        stats: int | None = None,
    ) -> None:
        """
        设置拥有量和统计量
        """
        await self.assure(uid, item_id)
        q = update(ItemInventory).where(ItemInventory.uid == uid)
        if count is not None:
            q = q.values({ItemInventory.count: count})
        if stats is not None:
            q = q.values({ItemInventory.stats: stats})
        await self.session.execute(q)

    async def get(self, uid: int, item_id: str) -> tuple[int, int]:
        """
        获得拥有量和统计量
        """
        await self.assure(uid, item_id)
        q = select(ItemInventory.count, ItemInventory.stats).where(
            ItemInventory.uid == uid,
            ItemInventory.item_id == item_id,
        )
        r = await self.session.execute(q)
        return r.tuples().one()

    async def give(self, uid: int, item_id: str, delta: int) -> int:
        """
        给玩家一定数量的物品，返回目前有的物品量
        """

        count, stats = await self.get(uid, item_id)
        count += delta
        stats += delta
        await self.set(uid, item_id, count, stats)
        return count

    async def use(self, uid: int, item_id: str, delta: int) -> int:
        """
        使用一定数量的物品，返回剩余的物品量
        如果存量不足，会报错
        """

        count, stats = await self.get(uid, item_id)
        count -= delta
        if count < 0:
            raise LackException(item_id, delta, count + delta)
        await self.set(uid, item_id, count, stats)
        return count

    async def get_dict(self, uid: int) -> dict[str, tuple[int, int]]:
        """
        获得拥有量和统计量的字典
        """
        q = select(
            ItemInventory.item_id, ItemInventory.count, ItemInventory.stats
        ).where(ItemInventory.uid == uid)
        r = await self.session.execute(q)
        d = {i: (c, s) for i, c, s in r.tuples().all()}
        return d
