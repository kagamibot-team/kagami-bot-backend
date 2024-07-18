from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..base.repository import DBRepository
from ..models import Global


class SettingRepository(DBRepository[Global]):
    """
    和游戏全局设置项有关的仓库
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Global)

    async def assure_one(self):
        """保证只有一个 GlobalSettings 对象"""
        query = select(func.count(Global.data_id))
        counts = (await self.session.execute(query)).scalar_one()

        if counts != 1:
            await self.session.execute(delete(Global))
            await self.add(Global())

    async def get_interval(self):
        """
        获取抓取间隔
        """
        await self.assure_one()
        return (await self.session.execute(select(Global.catch_interval))).scalar_one()

    async def set_interval(self, interval: int):
        """
        设置抓取间隔
        """
        await self.assure_one()
        await self.session.execute(update(Global).values(catch_interval=interval))

    async def get_last_version(self):
        """
        获取上次的版本号
        """
        await self.assure_one()
        return (
            await self.session.execute(select(Global.last_reported_version))
        ).scalar_one()

    async def set_last_version(self, version: str):
        """
        设置上次的版本号
        """
        await self.assure_one()
        await self.session.execute(update(Global).values(last_reported_version=version))
