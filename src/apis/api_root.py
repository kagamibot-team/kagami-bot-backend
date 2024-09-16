from fastapi import APIRouter
from pydantic import BaseModel

from src.apis.restful.base import APIWrapper
from src.base.onebot.onebot_tools import broadcast

router = APIRouter()


class BroadcastData(BaseModel):
    message: str
    is_admin: bool = False


@router.post("/broadcast")
async def broadcast_response(data: BroadcastData):
    await broadcast(message=data.message, require_admin=data.is_admin)
    return APIWrapper(data="ok.")


@router.get("/ping")
async def ping():
    return APIWrapper(data="pong")
