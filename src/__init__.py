"""
小镜 Bot 初始化的模块。当载入这个模块时，会自动开始初始化。
"""

import importlib
from pathlib import Path
import sys

from loguru import logger

from src.base.db import DatabaseManager
from src.base.event.event_dispatcher import EventDispatcher
from src.common.config import get_config


def load_secret_code(root: EventDispatcher):
    try:
        module = importlib.import_module("secret")
        res = module.init()
        root.link(res)
    except ModuleNotFoundError as e:
        logger.error("请检查是否下载了 secret 代码包！")
        if Path("./kagami-backend-secret").exists():
            logger.warning("你已经把 kagami-backend-secret 下载下来了！把它重命名为 secret 吧！")
        # raise e from e  # 这里抛出错误以后，将阻止程序启动。
        sys.exit(-1)


def init_src():
    from src.base.event.event_root import activate_root, root
    from src.services.items import register_inner_items

    from .apis.init import init_routers
    from .auto_reload import init
    from .services.achievements.old_version import \
        register_old_version_achievements

    activate_root(root)
    init()
    init_routers()
    register_old_version_achievements()
    register_inner_items()
    DatabaseManager.init_single()

    if get_config().load_secret_code:
        load_secret_code(root)
