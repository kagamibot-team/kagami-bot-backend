from src.imports import *
from src.imports import AsyncSession
from src.logic.catch_time import *
from .base.basic_test_case import SQLTestCase
from .base.mock_events import *
from nonebot.adapters.onebot.v11.message import Message, MessageSegment


class TestAdminCrud(SQLTestCase):
    async def createData(self, session: AsyncSession) -> None:
        self.createLevel("一星", 0.0, 1)

    async def test_add_level(self):
        bot = MockOnebot("0")

        await root.emit(
            GroupContext(
                MockOnebotGroupEvent(
                    5,
                    False,
                    Message([MessageSegment.text("::添加小哥 小测试 一星")]),
                    1,
                ),
                bot,
            )
        )

        query = select(Award.data_id)
        session = get_session()

        async with session.begin():
            res = (await session.execute(query)).scalars().all()
            self.assertEqual(len(res), 1)
