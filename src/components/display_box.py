import PIL
import PIL.Image


from src.common.draw.images import loadImage
from src.common.draw.shapes import applyMask, roundedRectangleMask, drawRoundedRectangleWithScalar
from src.common.draw.tools import hex_to_rgb, rgb_to_hex, mix_color


async def _display_box(color: str, central_image: str) -> PIL.Image.Image:
    image = await loadImage(central_image)
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
        image_new = PIL.Image.open("./res/new.png")
        image_new = image_new.convert("RGBA")

        image.paste(image_new, (88, 0), image_new)

    return image