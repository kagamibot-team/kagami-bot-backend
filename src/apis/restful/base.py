from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel


class StatusCode(Enum):
    ok = 0
    error = 1


T = TypeVar("T")


class APIWrapper(BaseModel, Generic[T]):
    code: StatusCode = StatusCode.ok
    msg: str = ""
    data: T
