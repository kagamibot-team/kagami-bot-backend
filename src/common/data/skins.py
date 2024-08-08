import os

from src.common.download import download, writeData


async def downloadSkinImage(sid: int, url: str):
    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "skins", f"{sid}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    await writeData(await download(url), _path())

    return _path()
