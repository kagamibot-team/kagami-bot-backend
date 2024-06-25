# import asyncio
# from src.imports import *
# from .base.basic_test_case import SQLTestCase


# class TestMultiThread(SQLTestCase):
#     """
#     测试一下，同时执行一些任务会不会导致意外的异常
#     """

#     async def test_two_session(self):
#         session1 = get_session()
#         session2 = get_session()

#         async def task(session: AsyncSession, delay: float, time: float):
#             await asyncio.sleep(delay)
#             async with session.begin():
#                 await asyncio.sleep(time)

#         evt_loop = asyncio.get_event_loop()
#         task1 = evt_loop.create_task(task(session1, 0, 1))
#         task2 = evt_loop.create_task(task(session2, 0.5, 1))

#         await task1
#         await task2

#     async def test_two_session_commit(self):
#         async def task(session: AsyncSession, delay: float, time: float):
#             await asyncio.sleep(delay)
#             async with session.begin():
#                 await session.execute(insert(Level).values(name=str(delay)))
#                 await asyncio.sleep(time)
#                 await session.commit()

#         evt_loop = asyncio.get_event_loop()

#         tasks: list[asyncio.Task[None]] = []

#         for i in range(10):
#             ts = evt_loop.create_task(task(get_session(), i / 10, 1))
#             tasks.append(ts)

#         for t in tasks:
#             await t

#     async def test_two_session_flush(self):
#         async def task(session: AsyncSession, delay: float, time: float):
#             await asyncio.sleep(delay)
#             async with session.begin():
#                 await session.execute(insert(Level).values(name=str(delay)))
#                 (await session.execute(select(Level.data_id))).scalars().all()
#                 await asyncio.sleep(time)
#                 await session.flush()
#                 (await session.execute(select(Level.data_id))).scalars().all()
#                 await asyncio.sleep(time)
#                 (await session.execute(select(Level.data_id))).scalars().all()
#                 await session.commit()

#         evt_loop = asyncio.get_event_loop()

#         tasks: list[asyncio.Task[None]] = []

#         for i in range(10):
#             ts = evt_loop.create_task(task(get_session(), i / 10, 1))
#             tasks.append(ts)

#         for t in tasks:
#             await t
