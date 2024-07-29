"""
小镜 Bot 初始化的模块。当载入这个模块时，会自动开始初始化。
"""

from auto_reload import init
from src.base.event.event_root import activate_root, root

activate_root(root)
init()
