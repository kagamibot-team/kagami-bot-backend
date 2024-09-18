from pathlib import Path
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.apis.restful.base import APIWrapper
from src.base.onebot.onebot_tools import broadcast

router = APIRouter()


class BroadcastData(BaseModel):
    message: str
    is_admin: bool = False


def log_stream():
    with open(Path("./data/log.log"), "r", encoding="utf-8") as log_file:
        log_file.seek(0, 2)
        while True:
            line = log_file.readline()
            if line:
                yield f"data: {line}\n\n"
            else:
                time.sleep(0.1)


@router.post("/broadcast")
async def broadcast_response(data: BroadcastData):
    await broadcast(message=data.message, require_admin=data.is_admin)
    return APIWrapper(data="ok.")


@router.get("/ping")
async def ping():
    return APIWrapper(data="pong")


@router.get("/logs")
async def sse_logs():
    """
    这是一个 SSE 接口，用于传输日志
    """
    return StreamingResponse(log_stream(), media_type="text/event-stream")
