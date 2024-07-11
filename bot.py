"""
小镜 Bot 的主程序。请直接运行它。
"""

# 当在 Windows 环境连接远程的 PostgreSQL 数据库时，启用下面两行
# import asyncio
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

from alembic import command
from alembic.config import Config


def pre_init():
    """
    在小镜启动之前进行的操作，主要是创建需要使用的文件夹
    """

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


def init():
    """
    初始化 bot，并加载所有需要的东西，包括检查数据库等
    """

    pre_init()

    # 初始化 Nonebot 对象
    nonebot.init()

    # 加载驱动器
    driver = nonebot.get_driver()
    driver.register_adapter(OneBotV11Adapter)  # type: ignore

    if not os.path.exists("./data/db.sqlite3"):
        with open("./data/db.sqlite3", "wb") as _:
            pass


    nonebot.logger.info("检查数据库状态")
    config = Config("./alembic.ini")
    command.upgrade(config, "head")

    nonebot.logger.info("正在检测数据表的更改")
    command.check(config)

    nonebot.logger.info("数据库没问题了")

    # 需要在 Nonebot 初始化完成后，才能导入插件内容
    __import__("src")


if __name__ == "__main__":
    init()
    nonebot.run()
