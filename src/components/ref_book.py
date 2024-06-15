import PIL
import PIL.Image

from src.common.draw.texts import Fonts, drawLimitedBoxOfTextWithScalar
from src.components.display_box import display_box


async def ref_book_box(title: str, notation: str, color: str, imgUrl: str):
    box = await display_box(color, imgUrl)

    bottomTitle = await drawLimitedBoxOfTextWithScalar(
        title,
        180,
        "center",
        "center",
        24,
        "#FFFFFF",
        Fonts.HARMONYOS_SANS_BLACK,
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