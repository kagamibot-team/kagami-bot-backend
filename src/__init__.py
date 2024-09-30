"""
小镜 Bot 初始化的模块。当载入这个模块时，会自动开始初始化。
"""

import importlib

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
        raise e from e  # 这里抛出错误以后，将阻止程序启动。


def init_src():
    from src.base.event.event_root import activate_root, root

    from .apis.init import init_routers
    from .auto_reload import init
    from .services.achievements.old_version import \
        register_old_version_achievements

    activate_root(root)
    init()
    init_routers()
    register_old_version_achievements()
    DatabaseManager.init_single()

    if get_config().load_secret_code:
        load_secret_code(root)
