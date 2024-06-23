import time
from typing import Any
from pydantic import BaseModel, TypeAdapter

from src.common.dataclasses.catch_data import PickDisplay


class CatchHistory(BaseModel):
    caught_time: float
    displays: dict[int, PickDisplay]
    uid: int
    qqid: int


CatchHistoryBuilder = TypeAdapter(CatchHistory)


class CatchHistoryContainer:
    dicts: dict[int, list[CatchHistory]]

    def dumps(self) -> dict[int, list[dict[str, Any]]]:
        return {k: [v.model_dump() for v in vs] for k, vs in self.dicts.items()}

    def __init__(self) -> None:
        self.dicts = {}

    def get_records(self, group_id: int) -> list[CatchHistory]:
        self._update()

        if group_id in self.dicts.keys():
            return self.dicts[group_id]
        return []

    def add_record(self, group_id: int, record: CatchHistory):
        self._update()

        if group_id in self.dicts.keys():
            self.dicts[group_id].append(record)
        else:
            self.dicts[group_id] = [record]

    def _update(self):
        now = time.time()
        threshold = now - 86400

        for gid in self.dicts.keys():
            self.dicts[gid] = [
                ch for ch in self.dicts[gid] if ch.caught_time >= threshold
            ]


catch_history_list = CatchHistoryContainer()


__all__ = ["CatchHistory", "CatchHistoryContainer", "catch_history_list"]
