# 当在 Windows 环境连接远程的 PostgreSQL 数据库时，启用下面两行
# import asyncio
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import nonebot

from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.console.adapter import Adapter as ConsoleAdapter

nonebot.init()


# 加载驱动器
driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter) # type: ignore
driver.register_adapter(ConsoleAdapter) # type: ignore


nonebot.load_plugin('src')


if __name__ == '__main__':
    nonebot.run()
