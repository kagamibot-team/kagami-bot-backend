import functools

import nonebot
from loguru import logger

from src.base.db import manual_checkpoint
from src.base.event_timer import addInterval
from src.common.config import config

driver = nonebot.get_driver()


@driver.on_startup
async def _():
    @functools.partial(addInterval, config.autosave_interval, skip_first=True)
    async def _():
        await manual_checkpoint()
        logger.info("数据库自动保存指令执行完了。")
