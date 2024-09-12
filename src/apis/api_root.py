from enum import Enum
from typing import Generic, TypeVar
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


T = TypeVar("T")


class StatusCode(Enum):
    ok = 0
    error = 1


class APIWrapper(BaseModel, Generic[T]):
    code: StatusCode = StatusCode.ok
    msg: str = ""
    data: T


class Ping(APIWrapper[str], BaseModel):
    data: str = "pong"


@router.get("/ping")
async def ping():
    return Ping()
