from pathlib import Path

import nonebot
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from nonebot.drivers.fastapi import Driver as FastAPIDriver

from .api_root import router as api_router
from .render_ui import router as render_ui_router
from .webhook import router as webhook_router

_nb_driver = nonebot.get_driver()

assert isinstance(_nb_driver, FastAPIDriver)

app = _nb_driver.server_app

sub_app = FastAPI()
sub_app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:5173", "localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_routers():
    """
    将所有内部 API 绑定上来
    """
    sub_app.include_router(render_ui_router)
    app.mount("/kagami", sub_app)
    app.mount("/kagami-res", StaticFiles(directory=Path("./res/")), name="res")
    app.include_router(webhook_router, prefix="/kagami-webhook")
    app.include_router(api_router, prefix="/kagami-api")
