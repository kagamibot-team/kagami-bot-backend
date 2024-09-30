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

    # ================
    # |  数据库设置  |
    # ================

    db_type: Literal["sqlite", "postgresql"] = "sqlite"
    "使用的数据库类型"

    autosave_interval: float = 600
    """
    SQLite 数据库自动保存间隔，为负数时不自动保存，单位秒
    """

    sqlite_dbname: str = "db.sqlite3"
    "SQLite 数据库的文件名"

    pg_username: str = "postgresql"
    "PG 数据库用户名"

    pg_password: str = "123456"
    "PG 数据库密码"

    pg_host: str = "localhost"
    "PG 数据库主机"

    pg_port: int = 5432
    "PG 数据库端口"

    pg_dbname: str = "kagami"
    "PG 数据库名字"

    # ================
    # | 消息队列设置 |
    # ================

    enable_rabbitmq_messages: bool = False
    "未来将会投入使用的选项，是否接收来自 RabbitMQ 的消息"

    rabbitmq_host: str = "127.0.0.1"
    "消息队列服务器地址"

    rabbitmq_port: int = 5672
    "消息队列服务器端口"

    rabbitmq_account: str = ""
    "消息队列服务器帐号"

    rabbitmq_password: str = ""
    "消息队列服务器密码"

    rabbitmq_virtual_host: str = "/"
    "消息队列的虚拟主机地址"

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

    reload_info_interval: int = 60
    "刷新群成员信息的间隔，单位秒，小于等于 0 则不刷新"

    # ==================
    # |  图片渲染设置  |
    # ==================

    browser: Literal["chrome", "firefox"] = "chrome"
    "使用什么浏览器"

    use_fake_browser: bool = False
    "是否使用假渲染器"

    renderer: Literal["basic", "service"] = "basic"
    "是否启用基于消息队列的渲染模式"

    frontend_dist: str = "./frontend/"
    "前端文件的地址"

    browser_count: int = 3
    "打开的浏览器数量"

    render_host: str = "127.0.0.1"
    "渲染访问的主机，默认是指向当前启动的页面"

    render_port: int = 0
    "渲染访问的端口，为 0 则使用当前 Nonebot 的端口"

    clean_browser_interval: int = 120
    "检查浏览器是否启动的时间间隔，单位秒，小于等于 0 则不检查"

    render_max_fail: int = 3
    "渲染器至多允许失败多少次，小于 0 则允许无限重试"

    # ===================
    # |  Web Hook 设置  |
    # ===================

    enable_web_hook: bool = False
    "是否启用 Web Hook"

    bot_start_webhook: str = ""
    "Bot 启动时发送的 Web Hook"

    bot_send_message_fail_webhook: str = ""
    "Bot 发送消息失败太多次数时发送的 Web Hook"

    send_message_fail_report_limit: int = 8
    "发送消息失败多少次后发送 Web Hook"

    # ============
    # | 安全设置 |
    # ============

    load_secret_code: bool = False
    "是否尝试加载隐藏代码"

    salt: str = ""
    """
    用于合成小哥时得到随机数的盐，你可以理解成地图种子。
    在生产环境，为保证小哥配方不会被破解，请设置一个奇怪的值
    （老 盐 同 志）
    """

    # ================
    # |  Properties  |
    # ================

    @property
    def frontend_path(self):
        return Path(self.frontend_dist)

    @property
    def sqlalchemy_database_url(self) -> str:
        "数据库 URI"
        if self.db_type == "sqlite":
            return f"sqlite+aiosqlite:///./data/{self.sqlite_dbname}"
        return f"postgresql+asyncpg:///{self.pg_username}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_dbname}"


def get_config() -> Config:
    return get_plugin_config(Config)


__all__ = ["get_config", "Config"]
