import datetime
import pytz


def now_datetime():
    return to_utc8(datetime.datetime.now())


def to_utc8(dt: datetime.datetime):
    return dt.astimezone(pytz.timezone("Asia/Shanghai"))


def timestamp_to_datetime(ts: float):
    return datetime.datetime.fromtimestamp(ts)


__all__ = ["to_utc8", "timestamp_to_datetime"]
