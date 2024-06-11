"""
关于渲染图片时所有的元件，在 Figma 中同步有定义
"""

import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageChops

from ..putils.threading import make_async
from ..putils.draw.texts import Fonts, drawLimitedBoxOfTextWithScalar

from .tools import *


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


async def _display_box(color: str, central_image: str) -> PIL.Image.Image:
    image = PIL.Image.open(central_image)
    image = image.convert("RGBA")
    image = image.resize((180, 144), PIL.Image.ADAPTIVE)
    image = await applyMask(image, await roundedRectangleMask(180, 144, 10))

    canvas = PIL.Image.new("RGBA", (180, 144), (255, 255, 255, 0))

    outerRect = await drawRoundedRectangleWithScalar(
        180, 144, 10, rgb_to_hex(mix_color(hex_to_rgb(color), (255, 255, 255), 0.35))
    )
    innerRect = await drawRoundedRectangleWithScalar(176, 140, 8, color)

    canvas.paste(outerRect, (0, 0), outerRect)
    canvas.paste(innerRect, (2, 2), innerRect)
    canvas.paste(image, (0, 0), image)

    return canvas


display_box_cache: dict[str, PIL.Image.Image] = {}


async def display_box(
    color: str, central_image: str, new: bool = False
) -> PIL.Image.Image:
    key = f"{color}-{central_image}"
    if key not in display_box_cache:
        display_box_cache[key] = await _display_box(color, central_image)

    image = display_box_cache[key].copy()

    if new:
        image_new = PIL.Image.open("./res/catch/NewIcon/新！标签.png")
        image_new = image_new.convert("RGBA")

        image.paste(image_new, (88, 0), image_new)

    return image


async def catch(
    title: str,
    description: str,
    image: str,
    stars: str,
    color: str,
    new: bool,
    notation: str,
) -> PIL.Image.Image:
    left_display = await display_box(color, image, new)
    rightDescription = await drawLimitedBoxOfTextWithScalar(
        description,
        567,
        "left",
        "left",
        19,
        "#ffffff",
        Fonts.FONT_HARMONYOS_SANS,
        16,
    )
    rightTitle = await drawLimitedBoxOfTextWithScalar(
        title,
        400,
        "left",
        "left",
        43,
        "#ffffff",
        Fonts.FONT_HARMONYOS_SANS_BLACK,
        36,
    )
    rightStar = await drawLimitedBoxOfTextWithScalar(
        stars,
        400,
        "right",
        "right",
        43,
        color,
        Fonts.FONT_HARMONYOS_SANS,
        28,
    )
    leftNotation = await drawLimitedBoxOfTextWithScalar(
        notation,
        170,
        "left",
        "left",
        57,
        "white",
        Fonts.SUPERMERCADO,
        48,
        strokeWidth=1,
        expandInnerBottom=5,
        expandBottom=5,
    )

    block = PIL.Image.new(
        "RGB", (800, max(180, rightDescription.height + 89)), "#9B9690"
    )
    block.paste(left_display, (18, 18), left_display)
    block.paste(rightTitle, (212, 18), rightTitle)
    block.paste(rightDescription, (212, 69), rightDescription)
    block.paste(rightStar, (379, 18), rightStar)
    block.paste(leftNotation, (28, 107), leftNotation)

    return block


async def refBookBox(title: str, notation: str, color: str, imgUrl: str):
    box = await display_box(color, imgUrl)

    bottomTitle = await drawLimitedBoxOfTextWithScalar(
        title,
        180,
        "center",
        "center",
        24,
        "#FFFFFF",
        Fonts.FONT_HARMONYOS_SANS_BLACK,
        20,
    )

    bottomNotation = await drawLimitedBoxOfTextWithScalar(
        notation,
        170,
        "left",
        "left",
        57,
        "white",
        Fonts.SUPERMERCADO,
        48,
        strokeWidth=2,
        expandInnerBottom=5,
        expandBottom=5,
        expandInnerLeft=5,
        expandLeft=5,
    )

    block = PIL.Image.new("RGB", (216, 210), "#9B9690")
    block.paste(box, (18, 18), box)
    block.paste(bottomTitle, (18, 170), bottomTitle)
    block.paste(bottomNotation, (23, 105), bottomNotation)

    return block


__all__ = ["display_box", "catch", "refBookBox"]
