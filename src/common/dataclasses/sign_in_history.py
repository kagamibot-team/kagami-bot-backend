import os
from pathlib import Path
import time
from nonebot import logger
from pydantic import BaseModel, ValidationError

from src.common.times import now_datetime, timestamp_to_datetime, to_utc8


class SignInHistory(BaseModel):
    last_check_time: float = 0
    group_record: dict[int, int] = {}

    def save(self, fp: str | Path = Path("./data/sign_in_history.json")):
        with open(fp, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json())

    def weak_load(self, fp: str | Path = Path("./data/sign_in_history.json")):
        if not os.path.exists(fp):
            return

        with open(fp, "r", encoding="utf-8") as f:
            try:
                de = self.model_validate_json(f.read())
                self.last_check_time = de.last_check_time
                self.group_record = de.group_record
            except ValidationError as e:
                logger.warning(f"在试图从硬盘持久化取签到记录的时候发生了问题 {e}")

    def _update(self):
        self.weak_load()
        de = (
            now_datetime().date()
            - to_utc8(timestamp_to_datetime(self.last_check_time)).date()
        )
        if de.days > 0:
            self.last_check_time = time.time()
            self.group_record = {}

    def sign(self, group_id: int):
        self._update()

        rec = self.group_record.get(group_id) or 0
        rec += 1
        self.group_record[group_id] = rec

        self.save()
        return rec


signInHistor = SignInHistory()
