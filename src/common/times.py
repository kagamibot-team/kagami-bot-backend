import datetime
import pytz


def now_datetime():
    return to_utc8(datetime.datetime.now())


def to_utc8(dt: datetime.datetime):
    tz = pytz.timezone("Asia/Shanghai")
    return dt.astimezone(tz)


def timestamp_to_datetime(ts: float):
    return datetime.datetime.fromtimestamp(
        ts, tz=datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    )


__all__ = ["to_utc8", "timestamp_to_datetime", "now_datetime"]
