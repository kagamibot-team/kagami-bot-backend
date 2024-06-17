import unittest


from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
)


from src.common.fast_import.database import *
from src.logic.catch_time import *


class TestCatch(unittest.IsolatedAsyncioTestCase):
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        session = self.session_factory()

        async with session.begin():
            user = User(qq_id=123)
            session.add(user)

            level = Level(name="一星", weight=1)
            award = Award(name="百变小哥")
            glob = Global(catch_interval=10)

            session.add(level)
            session.add(award)
            session.add(glob)

            await session.commit()

    async def asyncTearDown(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def test_catch_time(self):
        session = self.session_factory()

        async with session.begin():
            user = await session.execute(select(User).filter(User.qq_id == 123))
            user = user.scalar_one()

            user.pick_max_cache = 5
            user.pick_count_last_calculated = time.time() - 40
            user.pick_count_remain = 0

            await session.commit()

        async with session.begin():
            uid = await qid2did(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 4)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time(), delta=1)

    async def test_catch_time_2(self):
        session = self.session_factory()

        async with session.begin():
            user = await session.execute(select(User).filter(User.qq_id == 123))
            user = user.scalar_one()

            user.pick_max_cache = 3
            user.pick_count_last_calculated = time.time() - 40
            user.pick_count_remain = 0

            await session.commit()

        async with session.begin():
            uid = await qid2did(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 3)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time(), delta=1)


if __name__ == "__main__":
    unittest.main()
