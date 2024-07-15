from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""

    admin_id: int = -1
    "对 Bot 拥有绝对管理权的管理员（一员）"

    admin_groups: list[int] = []
    "小镜 Bot 的管理员群聊"

    my_name: list[str] = ["小镜", "柊镜"]
    "小镜 Bot 的名字"

    custom_replies: dict[str, str] = {}
    "在发送「小镜！！！」的时候，遇到特殊的 QQ 号，回复特殊的内容"

    predraw_images: int = 0
    "是否预先画好小哥的图片"

    sqlalchemy_database_url: str = "sqlite+aiosqlite:///./data/db.sqlite3"
    "数据库的 SQLAlchemy URI"

    enable_white_list: bool = False
    "是否启用仅在白名单群聊中才能够响应消息"

    white_list_groups: list[int] = []
    "白名单群聊"

    autosave_interval: float = 600
    "数据库自动保存间隔，在 SQLite 数据库时启用，为负数时不自动保存"


config = get_plugin_config(Config)
