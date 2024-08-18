"""
小镜 Bot 初始化的模块。当载入这个模块时，会自动开始初始化。
"""

from src.base.event.event_root import activate_root, root

from .auto_reload import init

from .apis.init import init_routers


activate_root(root)
init()
init_routers()
