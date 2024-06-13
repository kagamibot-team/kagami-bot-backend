import nonebot

from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.console.adapter import Adapter as ConsoleAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter) # type: ignore
driver.register_adapter(ConsoleAdapter) # type: ignore


nonebot.load_plugins('plugins')


if __name__ == '__main__':
    nonebot.run()
