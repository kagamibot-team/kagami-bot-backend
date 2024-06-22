from dataclasses import dataclass
import time

from nonebot import logger

from src.common.dataclasses.catch_data import PickDisplay


@dataclass
class CatchHistory:
    caught_time: float
    displays: dict[int, PickDisplay]
    uid: int
    qqid: int


class CatchHistoryContainer:
    dicts: dict[int, list[CatchHistory]]

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
            # logger.info(self.dicts[gid])
            self.dicts[gid] = [
                ch for ch in self.dicts[gid] if ch.caught_time >= threshold
            ]
            # logger.info(self.dicts[gid])


catch_histroy_list = CatchHistoryContainer()


__all__ = ["CatchHistory", "CatchHistoryContainer", "catch_histroy_list"]
