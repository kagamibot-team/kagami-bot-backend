from abc import ABC, abstractmethod

import PIL
import PIL.Image

from src.common.threading import make_async


class BaseImageMiddleware(ABC):
    """
    对 PILLOW 图像处理的中间件
    """

    @abstractmethod
    def _handle(self, image: PIL.Image.Image) -> PIL.Image.Image: ...

    async def handle(self, image: PIL.Image.Image) -> PIL.Image.Image:
        return await make_async(self._handle)(image)


class ResizeMiddleware(BaseImageMiddleware):
    """
    对 PILLOW 图像进行缩放
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def _handle(self, image: PIL.Image.Image) -> PIL.Image.Image:
        return image.resize((self.width, self.height))
