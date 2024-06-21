from src.common.download import download
from nonebot_plugin_alconna import Image, UniMessage


async def localize_image(image: Image) -> UniMessage[Image]:
    url = image.url
    if url is None:
        raise ValueError("传入的 Image 对象没有 url 属性")
    imgraw = await download(url)
    return UniMessage.image(raw=imgraw)


__all__ = ["localize_image"]
