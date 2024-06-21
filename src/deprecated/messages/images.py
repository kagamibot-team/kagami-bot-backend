import asyncio
import time

from ..db import *
from src.imports import *


GLOBAL_SCALAR = 1.5


Session = AsyncSession
driver = get_driver()


@driver.on_startup
async def preDrawEverything():
    if config.predraw_images == 0:
        logger.info("在开发环境中，跳过了预先绘制图像文件")
        return

    session = get_session()

    awards = await getAllAwards(session)
    begin = time.time()

    tasks: set[asyncio.Task[Any]] = set()

    async def _predraw(bg: str, img: str, ind: int, mx: int, nm: str):
        await display_box(bg, img)
        logger.info(f"{ind}/{mx} 预渲染完成了 {nm}")

    for ind, award in enumerate(awards):
        bg = award.level.color_code
        tasks.add(asyncio.create_task(_predraw(bg, award.img_path, ind + 1, len(awards), award.name)))

    skins = await getAllSkins(session)

    for ind, skin in enumerate(skins):
        bg = skin.award.level.color_code
        tasks.add(asyncio.create_task(_predraw(bg, skin.image, ind + 1, len(skins), skin.name)))
    
    for task in tasks:
        await task

    logger.info(f"已经完成了预先绘制图像文件，耗时 {time.time() - begin}")
