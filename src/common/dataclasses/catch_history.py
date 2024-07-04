import os
from pathlib import Path
import time
from nonebot import logger
from pydantic import BaseModel, TypeAdapter, ValidationError

from src.common.dataclasses.catch_data import PickDisplay


class CatchHistory(BaseModel):
    caught_time: float
    displays: dict[int, PickDisplay]
    uid: int
    qqid: int


CatchHistoryBuilder = TypeAdapter(CatchHistory)


class CatchHistoryContainer(BaseModel):
    dicts: dict[int, list[CatchHistory]] = {}

    def save(self, fp: str | Path = Path("./data/catch_history.json")):
        with open(fp, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json())

    def weak_load(self, fp: str | Path = Path("./data/catch_history.json")):
        if not os.path.exists(fp):
            return

        with open(fp, "r", encoding="utf-8") as f:
            try:
                self.dicts = self.model_validate_json(f.read()).dicts
            except ValidationError as e:
                logger.warning(f"在试图从硬盘持久化取喜报历史记录的时候发生了问题 {e}")

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

        self.save()

    def _update(self):
        self.weak_load()
        now = time.time()
        threshold = now - 86400

        for gid in self.dicts.keys():
            self.dicts[gid] = [
                ch for ch in self.dicts[gid] if ch.caught_time >= threshold
            ]


catch_history_list = CatchHistoryContainer()


__all__ = ["CatchHistory", "CatchHistoryContainer", "catch_history_list"]
