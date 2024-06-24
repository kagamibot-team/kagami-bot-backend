from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""

    # 对 Bot 拥有绝对管理权的管理员（一员）
    admin_id: int = -1

    # 允许管理 Bot 的小哥库等的各种事项的群
    admin_groups: list[int] = []

    # 我是谁
    my_name: list[str] = ["小镜", "柊镜"]

    # 在发送「小镜！！！」的时候，遇到特殊的 QQ 号，回复特殊的内容
    custom_replies: dict[str, str] = {}

    # 是否预先画好小哥的图片
    predraw_images: int = 0

    # 数据库的路径
    sqlalchemy_database_url: str = "sqlite+aiosqlite:///./data/db.sqlite3"

    # 是否启用仅在白名单群聊中才能够响应消息
    enable_white_list: bool = False

    # 白名单群聊
    white_list_groups: list[int] = []


config = get_plugin_config(Config)
