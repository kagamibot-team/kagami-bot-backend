from pydantic.dataclasses import dataclass


@dataclass
class UserTime:
    pickMax: int
    pickRemain: int
    pickLastUpdated: float
    interval: float
