from .base.basic_test_case import SQLTestCase
from .base.mock_events import MockUniMessageContext

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
        self.assertEqual(len(ctx.sent), 0)
