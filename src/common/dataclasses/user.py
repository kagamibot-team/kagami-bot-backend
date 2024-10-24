from pydantic.dataclasses import dataclass


@dataclass
class UserTime:
    slot_count: int
    slot_empty: int
    last_updated_timestamp: float
    interval: float
