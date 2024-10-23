from src.base.res import KagamiResourceManagers
from src.common.download import download


async def downloadSkinImage(sid: int, url: str):
    data = await download(url)
    KagamiResourceManagers.xiaoge.put(f"sid_{sid}.png", data)
