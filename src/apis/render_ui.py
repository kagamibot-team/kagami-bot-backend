"""
渲染用的 API
"""

from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
)
from loguru import logger
from pydantic import BaseModel

from src.base.onebot.onebot_tools import get_avatar_cached
from src.base.res import KagamiResourceManagers
from src.common.config import get_config
from src.ui.base.backend_pages import BackendDataManager

router = APIRouter()
manager = BackendDataManager()


FRONTEND_DIST = get_config().frontend_path
INDEX_PATH = FRONTEND_DIST / "index.html"


def backend_register_data(data: BaseModel | dict[str, Any]) -> str:
    return manager.register(data)


@router.get("/data/{data_id}/")
async def request_data(data_id: str):
    """
    向后台请求数据
    """
    data = manager.get(data_id)
    if data is None:
        return JSONResponse(
            {"status": "failed", "detail": "所请求的 data_id 不存在"}, status_code=404
        )
    return data


@router.get("/file/awards/{image_name}")
async def award_image(image_name: str):
    fp = Path("./data/awards/") / image_name
    if not fp.exists():
        return HTMLResponse("<html><body>404!</body></html>", 404)

    # [TODO] 未来，有图片缓存以后，改造成直接获得小哥图片的形式
    return FileResponse(fp)


@router.get("/file/skins/{image_name}")
async def skin_image(image_name: str):
    fp = Path("./data/skins/") / image_name
    if not fp.exists():
        return HTMLResponse("<html><body>404!</body></html>", 404)
    return FileResponse(fp)


@router.get("/file/temp/{image_name}")
async def temp_image(image_name: str):
    fp = Path("./data/temp/") / image_name
    if not fp.exists():
        return HTMLResponse("<html><body>404!</body></html>", 404)
    return FileResponse(fp)


@router.get("/file/registered/{image_name}")
async def registered_image(image_name: str):
    fp = KagamiResourceManagers.url_manager.registered_reverse.get(image_name)
    if fp is None or not fp.exists():
        return HTMLResponse("<html><body>404!</body></html>", 404)
    return FileResponse(fp)


@router.get("/pages/{path:path}")
async def serve_vue_app(path: str):
    file_path = FRONTEND_DIST / path

    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    if not INDEX_PATH.exists():
        logger.warning("未找到前端的 Index 文件，将渲染 Fallback 页面。")
        return HTMLResponse(
            Path("./res/frontend_fallback.html").read_text(encoding="utf-8")
        )
    return HTMLResponse((FRONTEND_DIST / "index.html").read_text(encoding="utf-8"))


@router.get("/file/avatar/qq/{qqid}/")
async def get_qq_avatar(qqid: int):
    img = await get_avatar_cached(qqid)
    return StreamingResponse(BytesIO(img))
