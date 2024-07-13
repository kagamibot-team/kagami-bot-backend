import io
from pathlib import Path

import PIL
import PIL.Image
from loguru import logger

from src.common.draw.tools import hex_to_rgb, mix_color, rgb_to_hex
from src.views.award import AwardInfo

from .basics import (
    apply_mask,
    draw_rounded_rectangle,
    paste_image,
    rounded_rectangle_mask,
)

DISPLAY_BOX_CACHE: dict[str, PIL.Image.Image] = {}


def _display_box(color: str, central_image: str | bytes | Path) -> PIL.Image.Image:
    if not isinstance(central_image, (str, Path)):
        image = PIL.Image.open(io.BytesIO(central_image)).convert("RGBA")
    else:
        image = PIL.Image.open(central_image).convert("RGBA")
        logger.info(f"图片 {central_image} 还没有被预渲染过，现在渲染。")
    image = image.resize((180, 144), PIL.Image.ADAPTIVE)
    image = apply_mask(image, rounded_rectangle_mask(180, 144, 10))

    canvas = PIL.Image.new("RGBA", (180, 144), (255, 255, 255, 0))

    outerRect = draw_rounded_rectangle(
        180, 144, 10, rgb_to_hex(mix_color(hex_to_rgb(color), (255, 255, 255), 0.35))
    )
    innerRect = draw_rounded_rectangle(176, 140, 8, color)

    paste_image(canvas, outerRect, 0, 0)
    paste_image(canvas, innerRect, 2, 2)
    paste_image(canvas, image, 0, 0)

    return canvas


def display_box(data: AwardInfo) -> PIL.Image.Image:
    """
    渲染 DisplayBox
    """

    cache_key = f"{data.level.color}-{hash(data.image)}"
    if cache_key not in DISPLAY_BOX_CACHE:
        DISPLAY_BOX_CACHE[cache_key] = _display_box(data.level.color, data.image)
    image = DISPLAY_BOX_CACHE[cache_key].copy()
    if data.new:
        image_new = PIL.Image.open("./res/new.png").convert("RGBA")
        paste_image(image, image_new, 88, 0)
    return image
