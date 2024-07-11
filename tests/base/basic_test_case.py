import unittest

from src.imports import *
from src.models.statics import level_repo


class SQLTestCase(unittest.IsolatedAsyncioTestCase):
    async def createData(self, session: AsyncSession) -> None:
        pass

    async def asyncSetUp(self) -> None:
        async with get_sql_engine().begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        session = get_session()

        async with session.begin():
            await self.createData(session)

        # 清空 level_repo，在重构之后再删掉这里
        level_repo.clear()

    async def asyncTearDown(self) -> None:
        async with get_sql_engine().begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        level_repo.clear()

    def createLevel(
        self,
        name: str,
        weight: float,
        data_id: int,
    ):
        level_repo.register(data_id, [], name, weight, "#000000", 0)

    def createAward(
        self,
        session: AsyncSession,
        name: str,
        level_id: int,
        data_id: int,
        catch_group: int | None = None,
    ):
        session.add(
            Award(
                name=name,
                level_id=level_id,
                data_id=data_id,
                catch_group=catch_group,
            )
        )


__all__ = ["SQLTestCase"]
