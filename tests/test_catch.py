import unittest


from src.imports import *
from src.imports import AsyncSession
from src.logic.catch import pickAwards
from src.logic.catch_time import *

from src.commands.onebot.catch import save_picks

from .base.basic_test_case import SQLTestCase


class TestCatch(SQLTestCase):
    async def createData(self, session: AsyncSession) -> None:
        award = Award(name="百变小哥", level=1, data_id=35)
        skin = Skin(name="小境", applied_award_id=35, data_id=1)
        glob = Global(catch_interval=10)

        self.createLevel("一星", 1.0, 1)
        session.add(award)
        session.add(glob)
        session.add(skin)

        uid = await get_uid_by_qqid(session, 123)
        await session.execute(
            update(User).where(User.data_id == uid).values(pick_max_cache=3)
        )

        await session.commit()

    async def test_catch_time_normal(self):
        session = get_session()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            await updateUserTime(session, uid, 0, time.time() - 25)
            await session.commit()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 2)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time() - 5, delta=1)

    async def test_catch_time_negative(self):
        session = get_session()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            await updateUserTime(session, uid, -1, time.time() - 20)
            await session.commit()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 1)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time(), delta=1)

    async def test_catch_time_over_max(self):
        session = get_session()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            await updateUserTime(session, uid, 4, time.time() - 20)
            await session.commit()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 4)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time(), delta=1)

    async def test_catch_time_overflow(self):
        session = get_session()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            await updateUserTime(session, uid, 2, time.time() - 20)
            await session.commit()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 3)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time(), delta=1)

    async def test_catch(self):
        session = get_session()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            await updateUserTime(session, uid, 3, time.time())
            await session.commit()

        async with session.begin():
            userTime = await calculateTime(session, uid)
            pickResult = await pickAwards(session, uid, 1)
            pickEvent = PicksEvent(uid, None, pickResult, session)
            await root.emit(pickEvent)

            self.assertFalse(await do_user_have_skin(session, uid, 1))

            pev = await save_picks(
                pickResult=pickResult,
                group_id=None,
                uid=uid,
                session=session,
                userTime=userTime,
            )
            self.assertAlmostEqual(pev.moneyUpdated, 20)
            await session.commit()

        async with session.begin():
            userTime = await calculateTime(session, uid)
            pickResult = await pickAwards(session, uid, 1)
            pickEvent = PicksEvent(uid, None, pickResult, session)
            await root.emit(pickEvent)

            self.assertTrue(await do_user_have_skin(session, uid, 1))


class TestCatchBan(SQLTestCase):
    async def createData(self, session: AsyncSession) -> None:
        self.createLevel("一星", 0.0, 1)

        award1 = Award(name="可以抽得到", level=1, data_id=1)
        award2 = Award(
            name="不可以抽到", level=1, data_id=100, is_special_get_only=True
        )

        session.add_all([award1, award2])
        await session.commit()

    async def test_catch_ban(self):
        session = get_session()

        async with session.begin():
            uid = await get_uid_by_qqid(session, 123)
            await updateUserTime(session, uid, 20, time.time())
            await session.commit()

        async with session.begin():
            pickResult = await pickAwards(session, uid, 1)

            for aid, _ in pickResult.awards.items():
                self.assertNotEqual(aid, 100)


if __name__ == "__main__":
    unittest.main()
