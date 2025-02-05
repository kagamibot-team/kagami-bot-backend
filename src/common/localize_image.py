from nonebot_plugin_alconna import Image, UniMessage

from src.base.message import image
from src.common.download import download


async def localize_image(img: Image) -> UniMessage[Image]:
    url = img.url
    if url is None:
        raise ValueError("传入的 Image 对象没有 url 属性")
    imgraw = await download(url)
    return image(imgraw)


__all__ = ["localize_image"]
