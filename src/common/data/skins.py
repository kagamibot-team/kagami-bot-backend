from src.base.res import KagamiResourceManagers
from src.common.download import download


async def download_skin_image(sid: int, url: str):
    data = await download(url)
    KagamiResourceManagers.xiaoge.put(f"sid_{sid}.png", data)
