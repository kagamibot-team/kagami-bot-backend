from sqlalchemy import insert, select, update

from ..base.repository import DBRepository
from ..models.models import Skin, SkinRecord


class SkinInventoryRepository(DBRepository):
    """
    和皮肤记录有关的仓库
    """

    async def do_user_have(self, uid: int, sid: int) -> bool:
        """获得一个用户是否拥有一个皮肤

        Args:
            uid (int): 用户的 ID
            sid (int): 皮肤的 ID

        Returns:
            bool: 是否拥有
        """

        query = select(SkinRecord.skin_id).filter(
            SkinRecord.user_id == uid,
            SkinRecord.skin_id == sid,
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none() is not None

    async def get_using(self, uid: int, aid: int) -> int | None:
        """获得一个用户正在挂载的皮肤

        Args:
            uid (int): 用户 ID
            aid (int): 小哥 ID

        Returns:
            int | None: 皮肤 ID，如果没有则留空
        """

        query = (
            select(SkinRecord.skin_id)
            .join(Skin, Skin.data_id == SkinRecord.skin_id)
            .filter(
                SkinRecord.user_id == uid,
                Skin.aid == aid,
                SkinRecord.selected == 1,
            )
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def clear(self, uid: int, aid: int):
        """取消挂载某个小哥所有的皮肤

        Args:
            uid (int): 用户 ID
            aid (int): 小哥 ID
        """

        await self.session.execute(
            update(SkinRecord)
            .where(
                SkinRecord.user_id == uid,
                SkinRecord.skin_id.in_(
                    select(Skin.data_id).join(SkinRecord).where(Skin.aid == aid)
                ),
            )
            .values({SkinRecord.selected: 0})
        )

    async def select(self, uid: int, sid: int) -> bool:
        """选择一个皮肤，如果没有这个皮肤，则不会生效
        Args:
            uid (int): 用户 ID
            sid (int): 皮肤 ID

        Returns:
            bool: 用户之前是否已经挂载了这个皮肤
        """

        aid = await self.session.scalar(select(Skin.aid).where(Skin.data_id == sid))
        assert aid is not None

        if await self.get_using(uid, aid) == sid:
            return True

        await self.clear(uid, aid)

        await self.session.execute(
            update(SkinRecord)
            .where(
                SkinRecord.user_id == uid,
                SkinRecord.skin_id == sid,
            )
            .values({SkinRecord.selected: 1})
        )
        return False

    async def give(self, uid: int, sid: int) -> bool:
        """给一个用户一个皮肤

        Args:
            uid (int): 用户 ID
            sid (int): 皮肤 ID

        Returns:
            bool: 用户在这之前是否拥有这个皮肤
        """

        if not await self.do_user_have(uid, sid):
            await self.session.execute(
                insert(SkinRecord).values(
                    {
                        SkinRecord.user_id: uid,
                        SkinRecord.skin_id: sid,
                    }
                )
            )
            await self.session.flush()
            return False
        return True

    async def get_using_dict(self, uid: int) -> dict[int, int]:
        """获得一个用户正在挂载的所有皮肤
        Args:
            uid (int): 用户 ID

        Returns:
            dict[int, int]: 皮肤 ID 的记录
        """

        query = (
            select(Skin.aid, SkinRecord.skin_id)
            .join(Skin, Skin.data_id == SkinRecord.skin_id)
            .filter(SkinRecord.user_id == uid, SkinRecord.selected == 1)
        )
        result = await self.session.execute(query)
        return dict(result.tuples().all())

    async def get_list(self, uid: int, aid: int | None = None) -> list[int]:
        """获取一个用户拥有的所有皮肤的列表

        Args:
            uid (int): 用户的 ID
            aid (int | None, optional): 限定的小哥的范围. Defaults to None.

        Returns:
            list[int]: 用户拥有的所有皮肤
        """

        query = select(SkinRecord.skin_id).filter(SkinRecord.user_id == uid)
        if aid is not None:
            query = query.join(Skin, Skin.data_id == SkinRecord.skin_id).filter(
                Skin.aid == aid
            )

        return list((await self.session.execute(query)).scalars())

    async def use(self, uid: int, aid: int, sid: int | None):
        """添加一个使用记录

        Args:
            uid (int): 用户 ID
            aid (int): 小哥的 ID
            sid (int | None): 皮肤的 ID，None 表示不使用
        """
        clear = (
            update(SkinRecord)
            .where(
                SkinRecord.user_id == uid,
                Skin.data_id == SkinRecord.skin_id,
                Skin.aid == aid,
            )
            .values({SkinRecord.selected: 0})
        )
        await self.session.execute(clear)
        if sid is not None:
            await self.session.execute(
                update(SkinRecord)
                .where(SkinRecord.skin_id == sid, SkinRecord.user_id == uid)
                .values({SkinRecord.selected: 1})
            )
