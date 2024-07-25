import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageChops

from utils.threading import make_async


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


__all__ = [
    "roundedRectangleMask",
    "drawRoundedRectangleWithScalar",
    "applyMask",
]
