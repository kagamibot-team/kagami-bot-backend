from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..base.repository import DBRepository
from ..models.models import Skin, SkinRecord


class SkinInventoryRepository(DBRepository[SkinRecord]):
    """
    和皮肤记录有关的仓库
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SkinRecord)

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
                Skin.award_id == aid,
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
                    select(Skin.data_id).join(SkinRecord).where(Skin.award_id == aid)
                ),
            )
            .values(selected=0)
        )

    async def select(self, uid: int, sid: int) -> bool:
        """选择一个皮肤，如果没有这个皮肤，则不会生效
        Args:
            uid (int): 用户 ID
            sid (int): 皮肤 ID

        Returns:
            bool: 用户之前是否已经挂载了这个皮肤
        """

        aid = await self.session.scalar(
            select(Skin.award_id).where(Skin.data_id == sid)
        )
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
            .values(selected=1)
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
                insert(SkinRecord).values(user_id=uid, skin_id=sid)
            )
            await self.session.flush()
            return False
        return True
