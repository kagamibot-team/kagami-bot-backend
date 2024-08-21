"""
渲染用的 API
"""

from io import BytesIO
from pathlib import Path
from sysconfig import get_platform, get_python_version

from fastapi import APIRouter
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
)
import nonebot
from pydantic import BaseModel

from src.base.onebot.onebot_api import get_avatar_image
from src.common.config import config
from src.common.lang.zh import get_latest_version
from src.ui.base.backend_pages import BackendDataManager

router = APIRouter()
manager = BackendDataManager()


FRONTEND_DIST = config.frontend_path


def backend_register_data(data: BaseModel) -> str:
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


@router.get("/metadata/")
async def request_meta_data():
    """
    向后台请求关于服务器的元数据
    """
    try:
        bot = nonebot.get_bot()
        onebot_meta = await bot.call_api("get_version_info")

        app_name: str = onebot_meta["app_name"]
        app_version: str = onebot_meta["app_version"]
    except:
        app_name: str = "未识别"
        app_version: str = "未识别"

    return {
        "app_name": app_name,
        "app_version": app_version,
        "kagami_version": get_latest_version(),
        "python_version": get_python_version(),
        "platform": get_platform(),
    }


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


@router.get("/pages/{path:path}")
async def serve_vue_app(path: str):
    file_path = FRONTEND_DIST / path

    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return HTMLResponse((FRONTEND_DIST / "index.html").read_text(encoding="utf-8"))


@router.get("/file/avatar/qq/{qqid}/")
async def get_qq_avatar(qqid: int):
    img = await get_avatar_image(qqid)
    return StreamingResponse(BytesIO(img))
