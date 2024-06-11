import PIL
import PIL.Image
import PIL.ImageDraw

from .typing import PILImage, PillowColorLike
from .images import addUpon


async def rectangle(
    base: PILImage,
    x: float,
    y: float,
    width: float,
    height: float,
    color: PillowColorLike,
):
    _rect = PIL.Image.new("RGB", (int(width), int(height)), color)

    await addUpon(base, _rect, x, y, 0, 0, width / int(width), height / int(height))


async def roundedRectangle(
    base: PILImage,
    x: float,
    y: float,
    width: float,
    height: float,
    radius: float,
    color: str,
):
    draw = PIL.ImageDraw.Draw(base)
    draw.rounded_rectangle(
        ((int(x), int(y)), (int(x + width), int(y + height))), radius, fill=color
    )

    return base
