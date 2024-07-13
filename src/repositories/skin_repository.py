from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.exceptions import ObjectNotFoundException
from src.models.models import SkinAltName

from ..base.repository import DBRepository
from ..models import Skin


class SkinRepository(DBRepository[Skin]):
    """
    皮肤的仓库
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Skin)

    async def get_all_images(self) -> dict[int, str]:
        qa = select(Skin.data_id, Skin.image)
        return {row[0]: row[1] for row in (await self.session.execute(qa)).tuples()}

    async def update_image(self, data_id: int, image: str | Path) -> None:
        u = update(Skin).where(Skin.data_id == data_id).values(image=str(image))
        await self.session.execute(u)

    async def get_info(self, sid: int) -> tuple[str, str, str]:
        """获得一个皮肤的信息

        Args:
            sid (int): 皮肤的 ID

        Returns:
            tuple[str, str, str]: 名字，描述，图
        """
        q = select(Skin.name, Skin.description, Skin.image).filter(Skin.data_id == sid)
        return (await self.session.execute(q)).tuples().one()

    async def get_sid(self, name: str) -> int | None:
        """根据名字获得皮肤的 ID

        Args:
            name (str): 名字

        Returns:
            int | None: 皮肤的 ID，不存在则为 None
        """

        q1 = select(Skin.data_id).where(Skin.name == name)
        a = (await self.session.execute(q1)).scalar_one_or_none()
        if a is None:
            q2 = select(SkinAltName.skin_id).where(SkinAltName.name == name)
            a = (await self.session.execute(q2)).scalar_one_or_none()

        return a
    
    async def get_sid_strong(self, name: str) -> int:
        """根据名字获得皮肤的 ID，如果不存在会抛出异常

        Args:
            name (str): 皮肤的名字

        Returns:
            int: 皮肤的 ID
        """
        s = await self.get_sid(name)
        if s is None:
            raise ObjectNotFoundException("皮肤", name)
        return s
