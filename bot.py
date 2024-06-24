# 当在 Windows 环境连接远程的 PostgreSQL 数据库时，启用下面两行
# import asyncio
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import os

import nonebot
from nonebot.adapters.console.adapter import Adapter as ConsoleAdapter
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

# 如果不存在目录，则开始构建
os.makedirs(os.path.join(".", "data"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "backup"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "awards"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "skins"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "kagami"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "temp"), exist_ok=True)


# 注册日志管理器
nonebot.logger.add(
    "./data/log.log",
    format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}",
    rotation="10 MB",
    level="INFO",
)


# 初始化 Nonebot 对象
nonebot.init()


# 加载驱动器
driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)  # type: ignore
driver.register_adapter(ConsoleAdapter)  # type: ignore


if not os.path.exists("./data/db.sqlite3"):
    with open("./data/db.sqlite3", "wb") as f:
        pass


from alembic import command
from alembic.config import Config

nonebot.logger.info("检查数据库状态")
config = Config("./alembic.ini")
command.upgrade(config, "head")


# 需要在 Nonebot 初始化完成后，才能导入插件内容
import src as _

if __name__ == "__main__":
    nonebot.run()
