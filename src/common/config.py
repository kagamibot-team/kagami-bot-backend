from pathlib import Path
from typing import Literal

from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """
    这里定义的是小镜 Bot 的配置文件的默认值
    如果需要更改，请在项目根目录创建 `.env` 文件
    然后指定对应的字段
    """

    # ==============
    # |  基本设置  |
    # ==============

    my_name: list[str] = ["小镜", "柊镜"]
    "小镜 Bot 的名字，用于呼叫 Bot"

    salt: str = ""
    """
    用于合成小哥时得到随机数的盐，你可以理解成地图种子。
    在生产环境，为保证小哥配方不会被破解，请设置一个奇怪的值
    （老 盐 同 志）
    """

    # ================
    # |  数据库设置  |
    # ================

    sqlalchemy_database_url: str = "sqlite+aiosqlite:///./data/db.sqlite3"
    "数据库 URI"

    autosave_interval: float = 600
    "数据库自动保存间隔，在 SQLite 数据库时启用，为负数时不自动保存，单位秒"

    # =========================
    # |  Onebot V11 API 设置  |
    # =========================

    admin_id: int = -1
    "对 Bot 拥有绝对管理权的管理员（一员）"

    admin_groups: list[int] = []
    "小镜 Bot 的管理员群聊"

    enable_white_list: bool = False
    "是否启用仅在白名单群聊中才能够响应消息"

    white_list_groups: list[int] = []
    "白名单群聊"

    limited_group: list[int] = []
    "在哪些群，功能受到限制"

    # ==================
    # |  图片渲染设置  |
    # ==================

    browser: Literal["chrome", "firefox"] = "chrome"
    "使用什么浏览器"

    use_fake_browser: bool = False
    "是否使用假渲染器"

    frontend_dist: str = "./frontend/"
    "前端文件的地址"

    browser_count: int = 1
    "打开的浏览器数量"

    render_host: str = "127.0.0.1"
    "渲染访问的主机，默认是指向当前启动的页面"

    render_port: int = 0
    "渲染访问的端口，为 0 则使用当前 Nonebot 的端口"

    # ================
    # |  Properties  |
    # ================

    @property
    def frontend_path(self):
        return Path(self.frontend_dist)


config = get_plugin_config(Config)


__all__ = ["config", "Config"]
