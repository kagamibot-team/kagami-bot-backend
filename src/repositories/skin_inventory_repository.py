from sqlalchemy import delete, insert, select, update
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

        query = (
            select(SkinRecord.skin_id)
            .filter(
                SkinRecord.user_id == uid,
                SkinRecord.skin_id == sid,
            )
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
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
