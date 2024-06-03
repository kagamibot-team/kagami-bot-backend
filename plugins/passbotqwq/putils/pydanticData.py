import json
import os
from typing import Generic, Type, TypeVar
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class PydanticDataManager(Generic[T]):
    data: dict[int, T]
    filePath: str
    cls: Type[T]

    def __init__(self, cls: Type[T], filePath: str) -> None:
        self.filePath = filePath
        self.cls = cls
        self.data = {}
        self.load()

    def load(self):
        if not os.path.exists(self.filePath):
            self.save()

        _data: dict[int, T] = {}  # type: ignore

        try:
            with open(self.filePath, "r", encoding="utf-8") as f:
                _element = json.load(f)

            assert type(_element) == dict

            for key in _element.keys():
                _data[int(key)] = self.cls(**_element[key])

            self.data = _data
        except Exception as e:
            return e

        return None

    def save(self):
        obj = {str(key): self.data[key].model_dump() for key in self.data.keys()}

        with open(self.filePath, "w", encoding="utf-8") as f:
            json.dump(obj, f)

    def set(self, key: int, value: T):
        self.data[key] = value
        self.save()

    def get(self, key: int):
        self.load()
        if key not in self.data.keys():
            self.data[key] = self.cls()

        return self.data[key]

    def open(self, key: int):
        return PydanticDataEditor(self, key)


class PydanticDataEditor(Generic[T]):
    base: PydanticDataManager[T]
    key: int
    d: T

    def __init__(self, base: PydanticDataManager[T], key: int) -> None:
        self.base = base
        self.key = key
        self.d = self.base.get(self.key)
    
    def __enter__(self):
        return self.d
    
    def __exit__(self, *_, **__):
        self.base.set(self.key, self.d)
        self.base.save()


class PydanticDataManagerGlobal(Generic[T]):
    data: T
    cls: Type[T]
    filePath: str

    def __init__(self, cls: Type[T], filePath: str) -> None:
        self.filePath = filePath
        self.cls = cls
        self.data = cls()
        self.load()

    def load(self):
        if not os.path.exists(self.filePath):
            self.save()

        try:
            with open(self.filePath, "r", encoding="utf-8") as f:
                _json = json.load(f)
                self.data = self.cls(**_json)
        except Exception as e:
            return e
        return None

    def save(self):
        with open(self.filePath, "w", encoding="utf-8") as f:
            f.write(self.data.model_dump_json())

    def set(self, value: T):
        self.data = value
        self.save()

    def get(self):
        return self.data
    
    def __enter__(self):
        return self.data
    
    def __exit__(self, *_, **__):
        self.save()
