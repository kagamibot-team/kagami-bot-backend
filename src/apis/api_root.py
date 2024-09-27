import os
import time
from pathlib import Path
from typing import Any, Generator, NoReturn

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.apis.restful.base import APIWrapper
from src.base.onebot.onebot_tools import broadcast
from src.ui.types.zhuagx import get_latest_version

router = APIRouter()


class BroadcastData(BaseModel):
    message: str
    is_admin: bool = False


import os
import time
from pathlib import Path


import os
import time
from pathlib import Path


def log_stream(log_file_path=Path("./data/log.log"), last_n_lines=50):
    with open(log_file_path, "rb") as log_file:
        log_file.seek(0, os.SEEK_END)
        block_size = 11

        lines = []
        buffer = b""


        # 第一步：往回追溯 50 行
        while len(lines) < last_n_lines + 1 and log_file.tell() > 0:
            # 判断现在能往回读多少，然后读
            seek_offset = min(block_size, log_file.tell())
            log_file.seek(-seek_offset, os.SEEK_CUR)
            buffer = log_file.read(seek_offset) + buffer

            # 刚刚读了，读回来
            log_file.seek(-seek_offset, os.SEEK_CUR)

            decoded_data = ""
            while len(buffer) > 0:
                try:
                    decoded_data = buffer.decode("utf-8")
                    break
                except UnicodeDecodeError as e:
                    # 这时候很有可能是开头的一个字符被截断，我们试着往前一个步长
                    log_file.seek(1, os.SEEK_CUR)
                    buffer = buffer[1:]

            lines = decoded_data.splitlines()

        # 这时第一行可能不完整，我们截断
        lines = lines[-last_n_lines + 1:]

        for line in lines:
            yield f"data: {line}\n\n"

        log_file.seek(0, os.SEEK_END)

        while True:
            line = log_file.readline()
            if line:
                yield f"data: {line.decode('utf-8')}\n\n"
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


@router.get("/version")
async def version():
    """
    获得当前环境的服务端版本
    """
    return APIWrapper(data=get_latest_version().version)
