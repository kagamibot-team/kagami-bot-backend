from src.base.onebot_basic import export_msg
from .base.basic_test_case import SQLTestCase
from .base.mock_events import MockOnebot, MockOnebotGroupEvent, MockUniMessageContext

from src.imports import *


class TestEvents(SQLTestCase):
    async def test_kagami(self):
        ctx = MockUniMessageContext(UniMessage().text("小镜！！！!!!"))
        self.assertIsInstance(ctx, UniMessageContext)
        await root.emit(ctx)
        self.assertEqual(len(ctx.sent), 1)
        self.assertEqual(len(ctx.sent[0]), 1)
        self.assertIsInstance(ctx.sent[0][0], Text)
        self.assertEqual(str(ctx.sent[0][0]), "在！！！!!!")

        ctx = MockUniMessageContext(UniMessage().text("小镜 我讨厌你"))
        self.assertIsInstance(ctx, UniMessageContext)
        await root.emit(ctx)
        logger.info(ctx.sent)
        self.assertEqual(len(ctx.sent), 0)

    async def test_commands(self):
        session = get_session()
        async with session.begin():
            self.createLevel("1", 1.0, 1)
            a = Award(level_id=1, name="2")
            session.add(a)

            await session.commit()

        bot = MockOnebot("0")
        ctx = GroupContext(
            MockOnebotGroupEvent(
                user_id=10000,
                to_me=False,
                message=export_msg(UniMessage().text("kz")),
                group_id=20000,
            ),
            bot,
        )
        self.assertIsInstance(ctx, UniMessageContext)
        await root.emit(ctx)
        logger.info([i[0] for i in bot.called_apis])
        self.assertGreater(len(bot.called_apis), 0)

        bot = MockOnebot("0")
        ctx = GroupContext(
            MockOnebotGroupEvent(
                user_id=10000,
                to_me=False,
                message=export_msg(UniMessage().text("zhuajd")),
                group_id=20000,
            ),
            bot,
        )
        self.assertIsInstance(ctx, UniMessageContext)
        await root.emit(ctx)
        logger.info([i[0] for i in bot.called_apis])
        self.assertGreater(len(bot.called_apis), 0)

        bot = MockOnebot("0")
        ctx = GroupContext(
            MockOnebotGroupEvent(
                user_id=10000,
                to_me=False,
                message=export_msg(UniMessage().text("kc")),
                group_id=20000,
            ),
            bot,
        )
        self.assertIsInstance(ctx, UniMessageContext)
        await root.emit(ctx)
        logger.info([i[0] for i in bot.called_apis])
        self.assertGreater(len(bot.called_apis), 0)

        bot = MockOnebot("0")
        ctx = GroupContext(
            MockOnebotGroupEvent(
                user_id=10000,
                to_me=False,
                message=export_msg(UniMessage().text("xb")),
                group_id=20000,
            ),
            bot,
        )
        self.assertIsInstance(ctx, UniMessageContext)
        await root.emit(ctx)
        logger.info([i[0] for i in bot.called_apis])
        self.assertGreater(len(bot.called_apis), 0)
