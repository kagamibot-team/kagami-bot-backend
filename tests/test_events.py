from .base.basic_test_case import SQLTestCase
from .base.mock_events import MockUniMessageContext

from src.imports import *


class TestEvents(SQLTestCase):
    async def test_kagami(self):
        ctx = MockUniMessageContext(UniMessage().text("小镜！！！"))
        self.assertIsInstance(ctx, UniMessageContext)
        await root.emit(ctx)
        self.assertEqual(len(ctx.sent), 1)
