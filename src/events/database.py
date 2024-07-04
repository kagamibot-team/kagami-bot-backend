import functools

from src.base.db import manual_checkpoint
from src.imports import *


@functools.partial(addInterval, config.autosave_interval, skip_first=False)
async def _():
    await manual_checkpoint()
    logger.info("数据库自动保存指令执行完了。")
