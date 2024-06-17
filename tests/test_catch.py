import unittest


from src.common.fast_import import *
from src.logic.catch import pickAwards
from src.logic.catch_time import *

from src.commands.onebot.catch import picks, save_picks
from tests.mock.contexts import MockGroupContext


from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot, Adapter


class TestCatch(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        async with sqlEngine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        session = get_session()

        async with session.begin():
            level = Level(name="一星", weight=1)
            award = Award(name="百变小哥", level=level)
            skin = Skin(name="小境", award=award)
            glob = Global(catch_interval=10)

            session.add(level)
            session.add(award)
            session.add(glob)
            session.add(skin)

            uid = await qid2did(session, 123)
            await session.execute(
                update(User).where(User.data_id == uid).values(pick_max_cache=3)
            )

            await session.commit()

    async def asyncTearDown(self) -> None:
        async with sqlEngine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def test_catch_time_normal(self):
        session = get_session()

        async with session.begin():
            uid = await qid2did(session, 123)
            await updateUserTime(session, uid, 0, time.time() - 25)
            await session.commit()

        async with session.begin():
            uid = await qid2did(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 2)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time() - 5, delta=1)

    async def test_catch_time_negative(self):
        session = get_session()

        async with session.begin():
            uid = await qid2did(session, 123)
            await updateUserTime(session, uid, -1, time.time() - 20)
            await session.commit()

        async with session.begin():
            uid = await qid2did(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 1)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time(), delta=1)

    async def test_catch_time_over_max(self):
        session = get_session()

        async with session.begin():
            uid = await qid2did(session, 123)
            await updateUserTime(session, uid, 4, time.time() - 20)
            await session.commit()

        async with session.begin():
            uid = await qid2did(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 4)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time(), delta=1)

    async def test_catch_time_overflow(self):
        session = get_session()

        async with session.begin():
            uid = await qid2did(session, 123)
            await updateUserTime(session, uid, 2, time.time() - 20)
            await session.commit()

        async with session.begin():
            uid = await qid2did(session, 123)
            ut = await calculateTime(session, uid)
            self.assertEqual(ut.pickRemain, 3)
            self.assertAlmostEqual(ut.pickLastUpdated, time.time(), delta=1)

    async def test_catch(self):
        session = get_session()

        async with session.begin():
            uid = await qid2did(session, 123)
            await updateUserTime(session, uid, 3, time.time())
            await session.commit()

        async with session.begin():
            userTime = await calculateTime(session, uid)
            pickResult = await pickAwards(session, uid, 1)
            pickEvent = PicksEvent(uid, pickResult, session)
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

            pev = await save_picks(pickResult=pickResult, uid=uid, session=session, userTime=userTime)
            self.assertAlmostEqual(pev.moneyUpdated, 20)
            await session.commit()
        
        async with session.begin():
            pickResult = await pickAwards(session, uid, 1)
            pickEvent = PicksEvent(uid, pickResult, session)
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
