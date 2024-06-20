import unittest

from src.common.fast_import import *


class SQLTestCase(unittest.IsolatedAsyncioTestCase):
    async def createData(self, session: AsyncSession) -> None:
        pass

    async def asyncSetUp(self) -> None:
        async with sqlEngine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        session = get_session()

        async with session.begin():
            await self.createData(session)

    async def asyncTearDown(self) -> None:
        async with sqlEngine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


__all__ = ["SQLTestCase"]
