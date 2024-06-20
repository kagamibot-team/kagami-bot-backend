from src.common.fast_import import *
from src.common.fast_import import AsyncSession
from .base.basic_test_case import SQLTestCase


class TestSkins(SQLTestCase):
    async def createData(self, session: AsyncSession) -> None:
        testLevel = Level(name="测试等级", data_id=1)
        award1 = Award(name="测试小哥1", level_id=1, data_id=1)
        award2 = Award(name="测试小哥2", level_id=1, data_id=2)
        award3 = Award(name="测试小哥3", level_id=1, data_id=3)

        skin1 = Skin(name="测试皮肤2.1", applied_award_id=2, data_id=1)
        skin2 = Skin(name="测试皮肤2.2", applied_award_id=2, data_id=2)
        skin3 = Skin(name="测试皮肤3.1", applied_award_id=3, data_id=3)

        session.add_all([testLevel, award1, award2, award3, skin1, skin2, skin3])
        await session.commit()
    
    async def test_give_skin(self):
        session = get_session()

        query = select(OwnedSkin.data_id).filter(OwnedSkin.skin_id == 1)

        async with session.begin():
            uid = await get_uid_by_qqid(session, 20000)
            
            await give_skin(session, uid, 2)
            await session.commit()

        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNone(res)

            await give_skin(session, uid, 1)
            await session.commit()

        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNotNone(res)
    
    async def test_set_skin(self):
        session = get_session()

        query = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 1)
        query2 = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 2)

        async with session.begin():
            uid = await get_uid_by_qqid(session, 20000)
            
            await give_skin(session, uid, 1)
            await give_skin(session, uid, 2)
            await give_skin(session, uid, 3)

            await set_skin(session, uid, 2)
            await session.commit()

        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNotNone(res)
            
            await set_skin(session, uid, 3)
            await session.commit()

        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNotNone(res)

            await set_skin(session, uid, 1)
            await session.commit()

        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNotNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNone(res)
    
    async def test_clear_skin(self):
        session = get_session()

        query = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 1)
        query2 = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 2)
        query3 = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 3)

        async with session.begin():
            uid = await get_uid_by_qqid(session, 20000)
            
            await give_skin(session, uid, 1)
            await give_skin(session, uid, 2)
            await give_skin(session, uid, 3)

            await set_skin(session, uid, 1)
            await session.commit()

        async with session.begin():
            await clear_skin(session, uid, 2)
            await session.commit()

        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNone(res)

            await set_skin(session, uid, 3)
            await session.commit()

        async with session.begin():
            await clear_skin(session, uid, 2)
            await session.commit()

        async with session.begin():
            res = (await session.execute(query3)).scalar_one_or_none()
            self.assertIsNotNone(res)

            await clear_skin(session, uid, 3)
            await session.commit()

        async with session.begin():
            res = (await session.execute(query3)).scalar_one_or_none()
            self.assertIsNone(res)
    
    async def test_switch_skin_of_award(self):
        session = get_session()

        query = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 1)
        query2 = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 2)
        query3 = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 3)

        async with session.begin():
            uid = await get_uid_by_qqid(session, 20000)
            
            await give_skin(session, uid, 1)
            await switch_skin_of_award(session, uid, 2)
            await session.commit()
        
        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNotNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNone(res)

            await switch_skin_of_award(session, uid, 2)
            await session.commit()
        
        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNone(res)

            await give_skin(session, uid, 2)
            await switch_skin_of_award(session, uid, 2)
            await session.commit()
        
        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNotNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNone(res)
            await switch_skin_of_award(session, uid, 2)
            await session.commit()
        
        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNotNone(res)
            await switch_skin_of_award(session, uid, 2)
            await session.commit()
        
        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNone(res)
            await switch_skin_of_award(session, uid, 2)
            await switch_skin_of_award(session, uid, 3)
            await switch_skin_of_award(session, uid, 1)
            await session.commit()
        
        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNotNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNone(res)
    
    async def test_switch_skin_of_award_2(self):
        session = get_session()

        query = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 1)
        query2 = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 2)
        query3 = select(UsedSkin.data_id).filter(UsedSkin.skin_id == 3)

        async with session.begin():
            uid = await get_uid_by_qqid(session, 20000)
            
            await give_skin(session, uid, 1)
            await give_skin(session, uid, 2)
            await give_skin(session, uid, 3)

            await session.commit()
        
        async with session.begin():
            await switch_skin_of_award(session, uid, 2)
            await switch_skin_of_award(session, uid, 3)
            await switch_skin_of_award(session, uid, 2)
            await session.commit()
        
        async with session.begin():
            res = (await session.execute(query)).scalar_one_or_none()
            self.assertIsNone(res)
            res = (await session.execute(query2)).scalar_one_or_none()
            self.assertIsNotNone(res)
            res = (await session.execute(query3)).scalar_one_or_none()
            self.assertIsNotNone(res)
