import unittest


from src.imports import *
from src.imports import AsyncSession
from src.logic.catch import pickAwards
from src.logic.catch_time import *

from src.commands.onebot.catch import save_picks

from .base.basic_test_case import SQLTestCase


class TestCatch(SQLTestCase):
    async def createData(self, session: AsyncSession) -> None:
        level = Level(name="一星", weight=1)
        award = Award(name="百变小哥", level=level, data_id=35)
        skin = Skin(name="小境", applied_award_id=35)
        glob = Global(catch_interval=10)

        session.add(level)
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

            kagami = (
                await session.execute(
                    select(Skin.data_id).filter(
                        Skin.name == "小境",
                        Skin.owned_skins.any(OwnedSkin.user_id == uid),
                    )
                )
            ).scalar_one_or_none()
            self.assertIsNone(kagami)

            pev = await save_picks(
                pickResult=pickResult, group_id=None, uid=uid, session=session, userTime=userTime
            )
            self.assertAlmostEqual(pev.moneyUpdated, 20)
            await session.commit()

        async with session.begin():
            userTime = await calculateTime(session, uid)
            pickResult = await pickAwards(session, uid, 1)
            pickEvent = PicksEvent(uid, None, pickResult, session)
            await root.emit(pickEvent)

            kagami = (
                await session.execute(
                    select(Skin.data_id).filter(
                        Skin.name == "小境",
                        Skin.owned_skins.any(OwnedSkin.user_id == uid),
                    )
                )
            ).scalar_one_or_none()
            self.assertIsNotNone(kagami)


if __name__ == "__main__":
    unittest.main()
