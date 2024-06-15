import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageChops

from src.common.threading import make_async

from .typing import Image, PillowColorLike
from .images import addUpon


async def rectangle(
    base: Image,
    x: float,
    y: float,
    width: float,
    height: float,
    color: PillowColorLike,
):
    _rect = PIL.Image.new("RGB", (int(width), int(height)), color)

    await addUpon(base, _rect, x, y, 0, 0, width / int(width), height / int(height))


async def roundedRectangle(
    base: Image,
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


@make_async
def roundedRectangleMask(
    width: int, height: int, radius: int, scalar: int = 2
) -> PIL.Image.Image:
    mask = PIL.Image.new("L", (width * scalar, height * scalar), 0)
    draw = PIL.ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, width * scalar, height * scalar), radius=radius * scalar, fill=255
    )
    return mask.resize((width, height), PIL.Image.ADAPTIVE)


async def drawRoundedRectangleWithScalar(
    width: int, height: int, radius: int, color: str, scalar: int = 2
):
    empty = PIL.Image.new("RGBA", (width, height), (255, 255, 255, 0))
    colored = PIL.Image.new("RGBA", (width, height), color)
    empty.paste(
        colored, (0, 0), await roundedRectangleMask(width, height, radius, scalar)
    )
    return empty


@make_async
def applyMask(image: PIL.Image.Image, mask: PIL.Image.Image):
    imageAlpha = image.convert("RGBA").split()[3]
    imageAlpha = PIL.ImageChops.multiply(imageAlpha, mask)
    image.putalpha(imageAlpha)

    return image
