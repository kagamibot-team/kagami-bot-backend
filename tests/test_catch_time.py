from unittest import TestCase

from src.common.dataclasses.user import UserTime
from src.logic.catch_time import recalculate_time


class TestCatchTime(TestCase):
    def test_catch_time_basic(self):
        data = UserTime(
            slot_count=10,
            slot_empty=5,
            last_updated_timestamp=0,
            interval=10,
        )
        data = recalculate_time(data, 21)
        self.assertEqual(data.slot_count, 10)
        self.assertEqual(data.slot_empty, 7)
        self.assertEqual(data.last_updated_timestamp, 20)
        self.assertEqual(data.interval, 10)

    def test_catch_time_absolute_full(self):
        data = UserTime(
            slot_count=10,
            slot_empty=5,
            last_updated_timestamp=0,
            interval=10,
        )
        data = recalculate_time(data, 55)
        self.assertEqual(data.slot_count, 10)
        self.assertEqual(data.slot_empty, 10)
        self.assertEqual(data.last_updated_timestamp, 55)
        self.assertEqual(data.interval, 10)

    def test_catch_time_overloaded(self):
        data = UserTime(
            slot_count=10,
            slot_empty=5,
            last_updated_timestamp=0,
            interval=10,
        )
        data = recalculate_time(data, 65)
        self.assertEqual(data.slot_count, 10)
        self.assertEqual(data.slot_empty, 10)
        self.assertEqual(data.last_updated_timestamp, 65)
        self.assertEqual(data.interval, 10)

    def test_catch_time_negative(self):
        data = UserTime(
            slot_count=10,
            slot_empty=-1,
            last_updated_timestamp=0,
            interval=10,
        )
        data = recalculate_time(data, 25)
        self.assertEqual(data.slot_count, 10)
        self.assertEqual(data.slot_empty, 1)
        self.assertEqual(data.last_updated_timestamp, 20)
        self.assertEqual(data.interval, 10)

    def test_catch_time_zero_interval(self):
        data = UserTime(
            slot_count=10,
            slot_empty=-5,
            last_updated_timestamp=0,
            interval=0,
        )
        data = recalculate_time(data, 114)
        self.assertEqual(data.slot_count, 10)
        self.assertEqual(data.slot_empty, 10)
        self.assertEqual(data.last_updated_timestamp, 114)
        self.assertEqual(data.interval, 0)

    def test_catch_time_is_full_before(self):
        data = UserTime(
            slot_count=10,
            slot_empty=12,
            last_updated_timestamp=0,
            interval=10,
        )
        data = recalculate_time(data, 10)
        self.assertEqual(data.slot_count, 10)
        self.assertEqual(data.slot_empty, 12)
        self.assertEqual(data.last_updated_timestamp, 10)
        self.assertEqual(data.interval, 10)

    def test_catch_time_absolutely_match(self):
        data = UserTime(
            slot_count=10,
            slot_empty=0,
            last_updated_timestamp=0,
            interval=10,
        )
        data = recalculate_time(data, 10)
        self.assertEqual(data.slot_count, 10)
        self.assertEqual(data.slot_empty, 1)
        self.assertEqual(data.last_updated_timestamp, 10)
        self.assertEqual(data.interval, 10)

    def test_catch_time_not_enough(self):
        data = UserTime(
            slot_count=10,
            slot_empty=0,
            last_updated_timestamp=0,
            interval=10,
        )
        data = recalculate_time(data, 5)
        self.assertEqual(data.slot_count, 10)
        self.assertEqual(data.slot_empty, 0)
        self.assertEqual(data.last_updated_timestamp, 0)
        self.assertEqual(data.interval, 10)
