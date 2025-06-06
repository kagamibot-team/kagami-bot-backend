import datetime

import pytz

from src.common.config import get_config


def now_datetime():
    return to_utc8(datetime.datetime.now())


def replace_tz(
    dt: datetime.datetime, tz: datetime.tzinfo = pytz.timezone("Asia/Shanghai")
):
    return dt.replace(tzinfo=tz)


def dttm(
    *,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
    minute: int | None = None,
    second: int | None = None,
):
    nt = now_datetime()
    year = year or nt.year
    month = month or nt.month
    day = day or nt.day
    hour = hour or nt.hour
    minute = minute or nt.minute
    second = second or nt.second

    return replace_tz(datetime.datetime(year, month, day, hour, minute, second))


def to_utc8(dt: datetime.datetime):
    tz = pytz.timezone("Asia/Shanghai")
    return dt.astimezone(tz)


def timestamp_to_datetime(ts: float):
    return datetime.datetime.fromtimestamp(
        ts, tz=datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    )


def is_holiday(time: datetime.datetime | None = None) -> bool:
    if time is None:
        time = now_datetime()
    return (time.date() - datetime.date(2023, 1, 1)).days % 7 in (0, 6)


def is_april_fool(time: datetime.datetime | None = None) -> bool:
    if time is None:
        time = now_datetime()
    return (
        (time.month == 4 and time.day == 1)
        or (time.month == 3 and time.day == 31)
        or (time.month == 4 and time.day == 2)
        or (time.month == 4 and time.day == 3)
        or (time.month == 4 and time.day == 4)
        or (time.month == 4 and time.day == 5)
        or (time.month == 4 and time.day == 6)
        or get_config().test_april_fool
    )


__all__ = ["to_utc8", "timestamp_to_datetime", "now_datetime", "replace_tz", "dttm"]
