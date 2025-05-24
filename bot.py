"""
小镜 Bot 的主程序。请直接运行它。
"""

# 当在 Windows 环境连接远程的 PostgreSQL 数据库时，启用下面两行
# import asyncio
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
import sys

import nonebot
import nonebot.config
import nonebot.drivers
import nonebot.drivers.fastapi
from loguru import logger
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

from alembic import command
from alembic.config import Config
from src import init_src

main_logger = logger.bind(name="kagami")


def pre_init():
    """
    在小镜启动之前进行的操作，主要是创建需要使用的文件夹
    """

    # 如果不存在目录，则开始构建
    os.makedirs(os.path.join(".", "data"), exist_ok=True)
    os.makedirs(os.path.join(".", "data", "backup"), exist_ok=True)
    os.makedirs(os.path.join(".", "data", "awards"), exist_ok=True)
    os.makedirs(os.path.join(".", "data", "skins"), exist_ok=True)
    os.makedirs(os.path.join(".", "data", "temp"), exist_ok=True)

    # 保证数据库文件本身存在
    if not os.path.exists("./data/db.sqlite3"):
        with open("./data/db.sqlite3", "wb") as _:
            pass

    # 清理所有的日志
    logger.remove()

    # 添加 stdout 日志
    logger.add(
        sys.stdout,
        level="DEBUG",
        format="[<green>{time:HH:mm:ss}</green> <level>{level}</level> <cyan>{name}</cyan>:<cyan>{line}</cyan>] <level>{message}</level>",
        filter=lambda record: not (record.get("name") or "").startswith("nonebot"),
    )

    # 注册日志管理器
    logger.add(
        "./data/log.log",
        format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}",
        rotation="10 MB",
        level="DEBUG",
    )

    # 添加另一个日志管理，用于记录错误
    logger.add(
        "./data/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}",
        rotation="10 MB",
        level="ERROR",
    )

    # 添加一个日志管理器，归档所有日志
    logger.add(
        "./data/archive.log",
        format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        level="DEBUG",
    )


def nb_init():
    """
    初始化 Nonebot 引擎。在 Nonebot 从项目中解耦之前，无法移除。
    """

    main_logger.success("NoneBot 引擎正在初始化")

    # 加载配置文件
    # TODO: 将这里的配置文件读取也解耦，完全自己实现，然后从 dotenv 开始转移到 config.json 中
    #       在未来，如果需要将小镜 BOT 核心迁移到 Docker 容器中，则需要保证能够通过 Docker 的
    #       环境变量注入来控制需要启用的选项。当然，未来也会支持直接在管理面板中直接更改一些配
    #       置，并且支持热更新。

    env = nonebot.config.Env()
    _env_file = f".env.{env.environment}"
    config = nonebot.config.Config(_env_file=(".env", _env_file))
    logger.configure(extra={"nonebot_log_level": config.log_level})

    # 加载 FastAPI 驱动器
    nonebot._driver = nonebot.drivers.fastapi.Driver(env, config)  # type: ignore


def init():
    """
    初始化 bot，并加载所有需要的东西，包括检查数据库等
    """

    pre_init()
    nb_init()

    # 加载驱动器
    driver = nonebot.get_driver()
    driver.register_adapter(OneBotV11Adapter)  # type: ignore

    main_logger.info("检查数据库状态")
    config = Config("./alembic.ini")
    command.upgrade(config, "head")

    main_logger.info("正在检测数据表的更改")
    command.check(config)
    main_logger.info("数据库没问题了")

    # 需要在 Nonebot 初始化完成后，才能导入插件内容
    init_src()


if __name__ == "__main__":
    init()
    nonebot.get_driver().run()  # type: ignore
