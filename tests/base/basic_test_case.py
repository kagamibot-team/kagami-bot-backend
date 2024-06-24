import unittest

from src.imports import *


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

    def createCatchGroup(
        self,
        session: AsyncSession,
        weight: float,
        time_limit_rule: str,
        data_id: int,
    ):
        session.add(
            CatchGroup(
                time_limit_rule=time_limit_rule,
                weight=weight,
                data_id=data_id,
            )
        )

    def createLevel(
        self,
        session: AsyncSession,
        name: str,
        weight: float,
        data_id: int,
    ):
        session.add(
            Level(
                name=name,
                weight=weight,
                data_id=data_id,
            )
        )

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
