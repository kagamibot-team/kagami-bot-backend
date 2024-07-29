import datetime
from abc import ABC, abstractmethod


class Schedule(ABC):
    @abstractmethod
    async def do(self) -> None:
        ...

    @abstractmethod
    def should_do(self, dt: datetime.datetime) -> bool:
        ...


class Timing(Schedule):
    last_time: datetime.datetime

    @property
    @abstractmethod
    def next(self) -> datetime.datetime:
        ...

    def should_do(self, dt: datetime.datetime) -> bool:
        return dt >= self.next
