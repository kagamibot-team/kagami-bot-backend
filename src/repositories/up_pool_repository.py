from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update

from src.base.exceptions import ObjectNotFoundException
from src.base.repository import DBRepository
from src.models.models import Award, User
from src.models.up_pool import (
    PackAwardRelationship,
    UpPool,
    UpPoolAwardRelationship,
    UpPoolInventory,
)


class UpPoolInfo(BaseModel):
    belong_pack: int
    name: str
    cost: int
    display: int
    enabled: bool


class PackRepository(DBRepository):
    async def get_main_aids_of_pack(self, pack: int) -> set[int]:
        """
        获得所有将主猎场设置为 pack 的小哥 ID
        """
        q = select(Award.data_id).filter(Award.main_pack_id == pack)
        r = await self.session.execute(q)
        return set(r.scalars())

    async def get_other_aids_of_pack(self, pack: int) -> set[int]:
        """
        使用 Relationship 表关联猎场和小哥的那些小哥 ID
        """
        q = select(PackAwardRelationship.aid).filter(PackAwardRelationship.pack == pack)
        r = await self.session.execute(q)
        return set(r.scalars())

    async def get_aids_without_main_pack(self) -> set[int]:
        """
        获得那些主要猎场不大于 0 的那些小哥，这些都是特殊的小哥
        """
        q = select(Award.data_id).filter(Award.main_pack_id <= 0)
        r = await self.session.execute(q)
        return set(r.scalars())

    async def get_aids_without_relationship(self) -> set[int]:
        """
        获得那些没有 Relationship 表关联猎场的那些小哥
        """
        q1 = select(Award.data_id)
        q2 = select(PackAwardRelationship.aid)
        r1 = await self.session.execute(q1)
        r2 = await self.session.execute(q2)
        return set(r1.scalars()) - set(r2.scalars())

    async def get_linked_packs(self, aid: int) -> set[int]:
        """
        获得一个小哥使用 Relationship 关联的猎场集合
        """
        q = select(PackAwardRelationship.pack).filter(PackAwardRelationship.aid == aid)
        r = await self.session.execute(q)
        return set(r.scalars())

    async def get_main_pack(self, aid: int) -> int:
        """
        获得一个小哥绑定的主猎场
        """
        q = select(Award.main_pack_id).filter(Award.data_id == aid)
        r = await self.session.execute(q)
        return r.scalar_one()

    async def set_main_pack(self, aid: int, pack: int):
        """
        设置一个小哥的主要猎场
        """
        q = update(Award).where(Award.data_id == aid).values({Award.main_pack_id: pack})
        await self.session.execute(q)

    async def add_linked_pack(self, aid: int, pack: int):
        """
        添加一个小哥的关联猎场
        """
        if pack not in await self.get_linked_packs(aid):
            q = insert(PackAwardRelationship).values(
                {
                    PackAwardRelationship.aid: aid,
                    PackAwardRelationship.pack: pack,
                }
            )
            await self.session.execute(q)
            await self.session.flush()

    async def remove_linked_pack(self, aid: int, pack: int):
        """
        删去一个小哥的关联猎场
        """
        q = delete(PackAwardRelationship).where(
            PackAwardRelationship.aid == aid, PackAwardRelationship.pack == pack
        )


class UpPoolRepository(DBRepository):
    async def create_pool(self, pack_id: int, name: str, cost: int):
        """创建一条猎场升级

        Args:
            pack_id (int): 它属于哪个猎场
            name (str): 猎场升级的名字
            cost (int): 购买这个升级需要的钱
        """
        await self.session.execute(
            insert(UpPool).values(
                {
                    UpPool.belong_pack: pack_id,
                    UpPool.name: name,
                    UpPool.cost: cost,
                    UpPool.display: 0,
                    UpPool.enabled: True,
                }
            )
        )

    async def remove_pool(self, upid: int):
        """删掉一个猎场升级

        Args:
            upid (int): 猎场升级的 ID
        """

        await self.session.execute(delete(UpPool).where(UpPool.data_id == upid))

    async def get_upid(self, name: str) -> int | None:
        """根据名字获得一个猎场的 ID

        Args:
            name (str): 猎场的名字

        Returns:
            (int | None): PIL，如果未找到则为 None
        """
        res = await self.session.execute(
            select(UpPool.data_id).filter(UpPool.name == name)
        )
        return res.scalar_one_or_none()

    async def get_upid_strong(self, name: str) -> int:
        """根据名字获得一个猎场的 ID

        Args:
            name (str): 猎场的名字

        Returns:
            int: PIL，如果未找到则会抛出 `ObjectNotFoundException`
        """
        upid = await self.get_upid(name)
        if upid is None:
            raise ObjectNotFoundException("猎场升级", name)
        return upid

    async def get_pool_info(self, upid: int) -> UpPoolInfo:
        """获得一个猎场升级的信息

        Args:
            upid (int): 猎场升级的 ID

        Returns:
            UpPoolInfo: 其基本信息
        """

        q = select(
            UpPool.belong_pack, UpPool.name, UpPool.cost, UpPool.display, UpPool.enabled
        ).filter(UpPool.data_id == upid)
        pack_id, name, cost, display, enabled = (
            (await self.session.execute(q)).tuples().one()
        )

        return UpPoolInfo(
            belong_pack=pack_id,
            name=name,
            cost=cost,
            display=display,
            enabled=enabled,
        )

    async def modify(
        self,
        upid: int,
        belong_pack: int | None = None,
        name: str | None = None,
        cost: int | None = None,
        display: int | None = None,
        enabled: bool | None = None,
    ):
        q = (
            update(UpPool)
            .where(UpPool.data_id == upid)
            .values(
                {
                    i: v
                    for i, v in (
                        {
                            UpPool.belong_pack: belong_pack,
                            UpPool.name: name,
                            UpPool.cost: cost,
                            UpPool.display: display,
                            UpPool.enabled: enabled,
                        }
                    ).items()
                    if v is not None
                }
            )
        )
        await self.session.execute(q)

    async def get_aids(self, upid: int) -> set[int]:
        """获得一个猎场升级中附加的小哥

        Args:
            upid (int): 猎场升级 ID

        Returns:
            set[int]: 小哥 ID 的集合
        """

        q = select(UpPoolAwardRelationship.aid).filter(
            UpPoolAwardRelationship.pool_id == upid
        )

        res = await self.session.execute(q)
        return set(res.scalars())

    async def get_award_names(self, upid: int) -> set[str]:
        """获得一个猎场升级中附加的小哥的名字

        Args:
            upid (int): 猎场升级 ID

        Returns:
            set[int]: 小哥 ID 的集合
        """

        q = (
            select(Award.name)
            .join(UpPoolAwardRelationship, UpPoolAwardRelationship.aid == Award.data_id)
            .filter(UpPoolAwardRelationship.pool_id == upid)
        )

        res = await self.session.execute(q)
        return set(res.scalars())

    async def add_aid(self, upid: int, aid: int) -> None:
        """
        向一个猎场升级中添加小哥
        """

        q = select(UpPoolAwardRelationship.data_id).filter(
            UpPoolAwardRelationship.aid == aid,
            UpPoolAwardRelationship.pool_id == upid,
        )

        d1 = (await self.session.execute(q)).scalar_one_or_none()
        if d1 is None:
            q = insert(UpPoolAwardRelationship).values(
                {
                    UpPoolAwardRelationship.aid: aid,
                    UpPoolAwardRelationship.pool_id: upid,
                }
            )
            await self.session.execute(q)
            await self.session.flush()

    async def remove_aid(self, upid: int, aid: int) -> None:
        """
        将一个小哥从猎场升级中去除
        """

        q = delete(UpPoolAwardRelationship).where(
            UpPoolAwardRelationship.pool_id == upid,
            UpPoolAwardRelationship.aid == aid,
        )
        await self.session.execute(q)
        await self.session.flush()

    async def get_using(self, uid: int) -> int | None:
        query = select(User.using_up_pool).filter(User.data_id == uid)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def set_using(self, uid: int, upid: int | None) -> None:
        query = (
            update(User).where(User.data_id == uid).values({User.using_up_pool: upid})
        )
        await self.session.execute(query)

    async def get_own(self, uid: int, pack_id: int | None = None) -> set[int]:
        query = select(UpPoolInventory.pool_id).filter(UpPoolInventory.uid == uid)
        if pack_id is not None:
            query = query.join(
                UpPool, UpPool.data_id == UpPoolInventory.pool_id
            ).filter(UpPool.belong_pack == pack_id)
        res = await self.session.execute(query)
        return set(res.scalars())

    async def add_own(self, uid: int, upid: int) -> None:
        if upid not in await self.get_own(uid):
            query = insert(UpPoolInventory).values(
                {
                    UpPoolInventory.pool_id: upid,
                    UpPoolInventory.uid: uid,
                }
            )
            await self.session.execute(query)
            await self.session.flush()

    async def remove_own(self, uid: int, upid: int) -> None:
        q = delete(UpPoolInventory).where(
            UpPoolInventory.uid == uid, UpPoolInventory.pool_id == upid
        )
        await self.session.execute(q)
        await self.session.flush()
