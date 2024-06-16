# 当在 Windows 环境连接远程的 PostgreSQL 数据库时，启用下面两行
# import asyncio
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import os
import nonebot

from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.console.adapter import Adapter as ConsoleAdapter

nonebot.init()


# 加载驱动器
driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)  # type: ignore
driver.register_adapter(ConsoleAdapter)  # type: ignore


# 需要在 Nonebot 初始化完成后，才能导入插件内容
import src as _


# 如果不存在目录，则开始构建
os.makedirs(os.path.join(".", "data"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "catch"), exist_ok=True)
# os.makedirs(os.path.join(".", "data", "catch", "awards"), exist_ok=True)
# os.makedirs(os.path.join(".", "data", "catch", "skins"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "awards"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "skins"), exist_ok=True)
os.makedirs(os.path.join(".", "data", "kagami"), exist_ok=True)


if __name__ == "__main__":
    nonebot.run()
