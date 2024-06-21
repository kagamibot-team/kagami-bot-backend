from src.imports import AsyncSession
from .base.basic_test_case import SQLTestCase

from src.imports import *
from src.logic.catch import pickAwards


# class TestRandomCatchProb(SQLTestCase):
#     async def createData(self, session: AsyncSession) -> None:
#         level1 = Level(name="l1", weight=1)
#         level2 = Level(name="l2", weight=10)

#         award1 = Award(name="a1", level=level1,data_id=1)
#         award2 = Award(name="a2", level=level2,data_id=2)

#         session.add(level1)
#         session.add(level2)
#         session.add(award1)
#         session.add(award2)

#         await session.commit()

#     async def test_catch_a_lot(self):
#         session = get_session()

#         async with session.begin():
#             uid = await get_uid_by_qqid(session, 123)
#             picks = (await pickAwards(session, uid, 1000)).awards

#             self.assertIn(1, picks.keys())
#             self.assertIn(2, picks.keys())

#             print(picks[1].delta / (picks[2].delta + picks[1].delta))

#             self.assertAlmostEqual(picks[1].delta / (picks[2].delta + picks[1].delta), 1 / 11, delta=0.01)
