import PIL
import PIL.Image

from .typing import PILImage, PillowColorLike
from .images import addUpon


def rectangle(base: PILImage, x: float, y: float, width: float, height: float, color: PillowColorLike):
    _rect = PIL.Image.new('RGB', (int(width), int(height)), color)

    addUpon(base, _rect, x, y, 0, 0, width / int(width), height / int(height))
