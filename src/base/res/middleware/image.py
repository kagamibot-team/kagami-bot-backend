from abc import ABC, abstractmethod

import PIL
import PIL.Image
import PIL.ImageFilter


class BaseImageMiddleware(ABC):
    """
    对 PILLOW 图像处理的中间件
    """

    @abstractmethod
    def handle(self, image: PIL.Image.Image) -> PIL.Image.Image: ...

    def to_string(self) -> str:
        return self.__class__.__name__


class ResizeMiddleware(BaseImageMiddleware):
    """
    对 PILLOW 图像进行缩放
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def handle(self, image: PIL.Image.Image) -> PIL.Image.Image:
        return image.resize((self.width, self.height))

    def to_string(self) -> str:
        return f"ResizeMiddleware({self.width}, {self.height})"


class BlurMiddleware(BaseImageMiddleware):
    """
    对 PILLOW 图像进行模糊
    """

    def __init__(self, radius: int):
        self.radius = radius

    def handle(self, image: PIL.Image.Image) -> PIL.Image.Image:
        return image.filter(PIL.ImageFilter.BoxBlur(self.radius))

    def to_string(self) -> str:
        return f"BlurMiddleware({self.radius})"
