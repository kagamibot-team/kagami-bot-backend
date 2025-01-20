from datetime import datetime, timedelta
import unittest

from src.commands.user.sleep import (
    SleepToLateException,
    UnknownArgException,
    parse_getup_time,
    update_sleep_data,
)


class TestSleepTimeParsing(unittest.TestCase):
    def test_parse_getup_time_normal(self):
        inp = ("明天早上 8 点起床",)
        expected_hour, expected_minute = 8, 0
        self.assertEqual(parse_getup_time(inp), (expected_hour, expected_minute))

    def test_parse_getup_time_specified_hour(self):
        inp = ("明天 10 点起床",)
        expected_hour, expected_minute = 10, 0
        self.assertEqual(parse_getup_time(inp), (expected_hour, expected_minute))

    def test_parse_getup_time_specified_hour_and_minute(self):
        inp = ("明天 9 点半起床",)
        expected_hour, expected_minute = 9, 30
        self.assertEqual(parse_getup_time(inp), (expected_hour, expected_minute))

    def test_parse_getup_time_unknown_arg(self):
        inp = ("明天下午 3 点起床",)
        with self.assertRaises(UnknownArgException):
            parse_getup_time(inp)

    def test_parse_getup_time_sleep_to_late(self):
        inp = ("明天 12 点起床",)
        with self.assertRaises(SleepToLateException):
            parse_getup_time(inp)


class TestSleepUpdateTime(unittest.TestCase):
    def test_update_sleep_data_success_within_one_day(self):
        now_time = datetime(2023, 10, 10, 22, 0, 0)  # 固定的测试时间
        last_time = now_time - timedelta(days=0.5)
        count = 5
        success = True

        expected_last_time, expected_count = update_sleep_data(
            now_time, last_time.timestamp(), count, success
        )

        self.assertEqual(expected_last_time, now_time.timestamp())
        self.assertEqual(expected_count, 6)

    def test_update_sleep_data_success_over_one_day(self):
        now_time = datetime(2023, 10, 10, 22, 0, 0)  # 固定的测试时间
        last_time = now_time - timedelta(days=2)
        count = 5
        success = True

        expected_last_time, expected_count = update_sleep_data(
            now_time, last_time.timestamp(), count, success
        )

        self.assertEqual(expected_last_time, now_time.timestamp())
        self.assertEqual(expected_count, 1)

    def test_update_sleep_data_failure(self):
        now_time = datetime(2023, 10, 10, 22, 0, 0)  # 固定的测试时间
        last_time = now_time - timedelta(days=0.5)
        count = 5
        success = False

        expected_last_time, expected_count = update_sleep_data(
            now_time, last_time.timestamp(), count, success
        )

        self.assertEqual(expected_last_time, now_time.timestamp())
        self.assertEqual(expected_count, 0)


if __name__ == "__main__":
    unittest.main()
