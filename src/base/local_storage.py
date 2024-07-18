from datetime import datetime
from enum import Enum
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, ValidationError

from src.common.times import now_datetime


class Action(Enum):
    catched = "抓到了"
    merged = "合成出了"
    gained = "获得了"


class XBRecord(BaseModel):
    """
    单条喜报的记录
    """

    time: datetime
    "喜报记录的时间"

    action: Action
    "这条喜报是关于什么的"

    data: str
    "喜报展示的信息"


class XBData(BaseModel):
    records: list[XBRecord] = []

    def expire(self):
        """
        清理掉过期了的喜报，默认喜报的过期时间是一天
        """

        current = now_datetime()
        self.records = [r for r in self.records if (current - r.time).days == 0]


class GroupSignInData(BaseModel):
    time: datetime = datetime(2024, 1, 1, 0, 0, 0)
    count: int = 0

    def expire(self):
        """
        当过去一天时，重置签到时间
        """

        current = now_datetime()
        if (current.date() - self.time.date()).days > 0:
            self.count = 0
            self.time = current


class LocalStorageData(BaseModel):
    ls_version: int = 1
    xbs: dict[str, dict[str, XBData]] = {}
    group_sign_in_data: dict[str, GroupSignInData] = {}

    def update(self):
        for ls in self.xbs.values():
            for e in ls.values():
                e.expire()
        for e in self.group_sign_in_data.values():
            e.expire()

    def get_group_xb(self, group: str | int):
        self.update()
        self.xbs.setdefault(str(group), {})
        return self.xbs[str(group)]

    def get_group_signin_count(self, group: str | int):
        self.update()
        self.group_sign_in_data.setdefault(str(group), GroupSignInData())
        return self.group_sign_in_data

    def add_xb(self, group: int | str, qqid: int | str, record: XBRecord):
        self.get_group_xb(group).setdefault(str(qqid), XBData())
        self.xbs[str(group)][str(qqid)].records.append(record)
        self.update()

    def sign(self, group: int | str):
        self.update()
        self.get_group_signin_count(str(group))
        self.group_sign_in_data[str(group)].count += 1
        return self.group_sign_in_data[str(group)].count


class LocalStorageManager:
    path: Path
    _data: LocalStorageData

    _instance: "LocalStorageManager | None" = None

    @staticmethod
    def instance():
        if LocalStorageManager._instance is None:
            raise RuntimeError("请先初始化 LocalStorageData 实例")
        return LocalStorageManager._instance

    @staticmethod
    def init():
        if LocalStorageManager._instance is not None:
            raise RuntimeError("LocalStorageData 实例已经初始化过了！")
        LocalStorageManager._instance = LocalStorageManager()

    def __init__(self, path: str | Path = Path("./data/localstorage.json")) -> None:
        self.path = Path(path)
        self._data = LocalStorageData()
        self.weak_load()

    @property
    def data(self):
        self.weak_load()
        self.save()
        return self._data

    def update(self):
        self._data.update()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(self._data.model_dump_json())

    def weak_load(self):
        if not self.path.exists():
            return

        with open(self.path, "r", encoding="utf-8") as f:
            try:
                self._data = LocalStorageData.model_validate_json(f.read())
            except ValidationError as e:
                logger.warning(f"在试图从硬盘持久化取喜报历史记录的时候发生了问题 {e}")


LocalStorageManager.init()


def get_localdata():
    return LocalStorageManager.instance().data


def save_localdata():
    LocalStorageManager.instance().save()
