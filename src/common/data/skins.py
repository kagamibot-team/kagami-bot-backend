import os

from src.base.res import KagamiResourceManagers
from src.common.download import download


async def downloadSkinImage(sid: int, url: str):
    data = await download(url)
    await KagamiResourceManagers.xiaoge.put(f"aid_{sid}.png", data)
