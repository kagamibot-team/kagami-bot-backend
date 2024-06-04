import PIL
import PIL.Image

from .typing import IMAGE, PILLOW_COLOR_LIKE
from .images import addUpon


def rectangle(base: IMAGE, x: float, y: float, width: float, height: float, color: PILLOW_COLOR_LIKE):
    _rect = PIL.Image.new('RGB', (int(width), int(height)), color)

    addUpon(base, _rect, x, y, 0, 0, width / int(width), height / int(height))
