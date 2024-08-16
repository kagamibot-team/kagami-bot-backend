"""
渲染用的 API
"""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from src.ui.base.backend_pages import BackendDataManager

router = APIRouter()
manager = BackendDataManager()


def backend_register_data(data: BaseModel) -> str:
    return manager.register(data)


@router.get("/data/{data_id}/")
async def request_data(data_id: str):
    """
    向后台请求数据
    """
    data = manager.get(data_id)
    if data is None:
        return {"status": "failed", "detail": "所请求的 data_id 不存在"}
    return {"status": "success", "detail": "", "data": data}


@router.get("/file/award/{image_name}")
async def award_image(image_name: str):
    fp = Path("./data/awards/") / image_name
    if not fp.exists():
        return HTMLResponse(
            Path("./res/html/404.html").read_text(encoding="utf-8"), 404
        )

    # [TODO] 未来，有图片缓存以后，改造成直接获得小哥图片的形式
    return FileResponse(fp)


@router.get("/file/skin/{image_name}")
async def skin_image(image_name: str):
    fp = Path("./data/skins/") / image_name
    if not fp.exists():
        return HTMLResponse(
            Path("./res/html/404.html").read_text(encoding="utf-8"), 404
        )
    return FileResponse(fp)


@router.get("/pages/{path:path}")
async def serve_vue_app(path: str):
    file_path = Path("./res/dist/") / path

    # If the requested file exists, serve it (e.g., JavaScript, CSS, images)
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return HTMLResponse(Path("./res/dist/index.html").read_text(encoding="utf-8"))
