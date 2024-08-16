from pathlib import Path

import nonebot
from fastapi.staticfiles import StaticFiles
from nonebot.drivers.fastapi import Driver as FastAPIDriver

from .render_ui import router as render_ui_router

_nb_driver = nonebot.get_driver()

assert isinstance(_nb_driver, FastAPIDriver)

app = _nb_driver.server_app


def init_routers():
    """
    将所有内部 API 绑定上来
    """
    app.include_router(render_ui_router, prefix="/kagami")
    app.mount("/kagami/res", StaticFiles(directory=Path("./res/")), name="res")
