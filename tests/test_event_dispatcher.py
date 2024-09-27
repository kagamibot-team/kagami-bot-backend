import asyncio
from unittest import IsolatedAsyncioTestCase

from src.base.event.event_dispatcher import EventDispatcher
from src.base.exceptions import KagamiStopIteration


class TestEventManager(IsolatedAsyncioTestCase):
    async def test_basic(self):
        dispatcher = EventDispatcher()

        received_str: list[str] = []
        received_number: list[complex] = []

        @dispatcher.listen(str)
        async def _(data: str):
            await asyncio.sleep(0.05)
            received_str.append(data)

        @dispatcher.listens(int, complex, float)
        async def _(data: complex):
            received_number.append(data)

        await dispatcher.emit("hello")
        await dispatcher.emit(123)
        await dispatcher.emit(45.6)
        await dispatcher.emit(7.8 + 9.1j)

        self.assertListEqual(received_str, ["hello"])
        self.assertListEqual(received_number, [123, 45.6, 7.8 + 9.1j])

        await dispatcher.throw("hi")
        self.assertListEqual(received_str, ["hello"])
        await asyncio.sleep(0.1)
        self.assertListEqual(received_str, ["hello", "hi"])

    async def test_sub_dispatchers(self):
        dispatcher1 = EventDispatcher()
        dispatcher2 = EventDispatcher()
        dispatcher3 = EventDispatcher()

        dispatcher1.link(dispatcher2)

        results1: set[str] = set()
        results2: set[str] = set()
        results3: set[str] = set()

        @dispatcher1.listen(str)
        async def _(data: str):
            await asyncio.sleep(0.05)
            results1.add(data)

        @dispatcher2.listen(str)
        async def _(data: str):
            await asyncio.sleep(0.05)
            results2.add(data)

        @dispatcher3.listen(str)
        async def _(data: str):
            await asyncio.sleep(0.05)
            results3.add(data)

        await dispatcher1.emit("message_from_1")
        await dispatcher2.throw("message_from_2")
        await dispatcher3.emit("message_from_3")

        await asyncio.sleep(0.1)

        self.assertSetEqual(results1, {"message_from_1", "message_from_2"})
        self.assertSetEqual(results2, {"message_from_1", "message_from_2"})
        self.assertSetEqual(results3, {"message_from_3"})

    async def test_exceptions(self):
        dispatcher = EventDispatcher()
        received_str: list[str] = []

        @dispatcher.listens(list[str], str)
        async def _(data: list[str] | str):
            self.assertNotIsInstance(data, list)
            assert not isinstance(data, list)
            received_str.append(data)

        await dispatcher.emit(["123", "234"])
        await dispatcher.emit("555666")
        self.assertListEqual(received_str, ["555666"])

        result_set: set[int] = set()

        @dispatcher.listen(int, priority=10)
        async def _(data: int):
            result_set.add(10000 + data)
            if data == 10:
                raise KagamiStopIteration()

        @dispatcher.listen(int)
        async def _(data: int):
            result_set.add(20000 + data)

        await dispatcher.emit(10)
        await dispatcher.emit(5)
        self.assertSetEqual(result_set, {10010, 10005, 20005})
