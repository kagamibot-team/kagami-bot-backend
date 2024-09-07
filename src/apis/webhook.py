from fastapi import APIRouter
from pydantic import BaseModel

from src.base.onebot.onebot_tools import broadcast

router = APIRouter()


class BroadcastData(BaseModel):
    message: str
    is_admin: bool = False


@router.post("/broadcast")
async def broadcast_response(data: BroadcastData):
    await broadcast(message=data.message, require_admin=data.is_admin)
    return "ok."
