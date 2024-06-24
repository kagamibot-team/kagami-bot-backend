from src.imports import *
from src.logic.catch_time import *

from .base.basic_test_case import SQLTestCase


class TestCatchGroup(SQLTestCase):
    def assertValidateTrue(self, rule: str, dt: datetime):
        self.assertTrue(CatchGroup.validate(rule, dt))

    def assertValidateFalse(self, rule: str, dt: datetime):
        self.assertFalse(CatchGroup.validate(rule, dt))

    async def test_catch_group_validate(self):
        dt = datetime(2010, 1, 2, 1, 3, 5)

        self.assertValidateTrue("* * * * * * *", dt)
        self.assertValidateTrue("2000-2020 * * * * * *", dt)
        self.assertValidateFalse("2012-2020 * * * * * *", dt)
        self.assertValidateTrue("2000-2010,2012-2020 * * * * * *", dt)
        self.assertValidateTrue("* 1 2 * * * 5", dt)
        self.assertValidateFalse("* 1 2 * * * 4", dt)

    async def test_catch_group_db(self):
        session = get_session()

        async with session.begin():
            self.createLevel(session, "t", 0, 1)
            self.createCatchGroup(session, 0, "", 1)
            self.createAward(session, "", 1, 1, 1)

            await session.commit()

        async with session.begin():
            await session.execute(delete(CatchGroup).where(CatchGroup.data_id == 1))
            await session.commit()

        async with session.begin():
            q = select(Award.data_id)
            s = (await session.execute(q)).scalars()
            self.assertSetEqual(set(s), {1})

            q = select(Award.catch_group)
            s = (await session.execute(q)).scalars()
            self.assertSetEqual(set(s), {None})

        async with session.begin():
            await session.execute(delete(Level).where(Level.data_id == 1))
            await session.commit()

        async with session.begin():
            q = select(Award.data_id)
            s = (await session.execute(q)).scalars()
            self.assertSetEqual(set(s), set())
