import PIL
import PIL.Image

from src.common.draw.texts import (
    Fonts,
    HorizontalAnchor,
    drawLimitedBoxOfTextClassic,
    drawLimitedBoxOfTextWithScalar,
)
from src.components.display_box import display_box


async def __title(text: str, color: str = "#FFFFFF"):
    return await drawLimitedBoxOfTextWithScalar(
        text,
        180,
        "center",
        "center",
        24,
        color,
        Fonts.HARMONYOS_SANS_BLACK,
        20,
        scalar=2,
    )


async def ref_book_box(title: str, notation: str, color: str, imgUrl: str):
    box = await display_box(color, imgUrl)

    bottomTitle = await __title(title)

    bottomNotation = await drawLimitedBoxOfTextClassic(
        text=notation,
        maxWidth=170,
        lineHeight=57,
        color="white",
        font=Fonts.MARU_MONICA,
        fontSize=48,
        strokeWidth=2,
        expandInnerBottom=5,
        expandBottom=5,
        expandInnerLeft=5,
        expandInnerRight=5,
        expandLeft=5,
        align=HorizontalAnchor.left,
    )

    block = PIL.Image.new("RGB", (216, 210), "#9B9690")
    block.paste(box, (18, 18), box)
    block.paste(bottomTitle, (18, 170), bottomTitle)
    block.paste(bottomNotation, (23, 105), bottomNotation)

    return block


async def skin_book(title: str, title2: str, notation: str, color: str, imgUrl: str):
    box = await display_box(color, imgUrl)

    bottomTitle = await __title(title)
    bottomTitle2 = await __title(title2, "#C4BEBD")

    bottomNotation = await drawLimitedBoxOfTextClassic(
        text=notation,
        maxWidth=170,
        lineHeight=57,
        color="white",
        font=Fonts.MARU_MONICA,
        fontSize=36,
        strokeWidth=2,
        expandInnerBottom=5,
        expandBottom=5,
        expandInnerLeft=5,
        expandInnerRight=5,
        expandLeft=5,
        align=HorizontalAnchor.left,
    )

    block = PIL.Image.new("RGB", (216, 234), "#9B9690")
    block.paste(box, (18, 18), box)
    block.paste(bottomTitle, (18, 170), bottomTitle)
    block.paste(bottomTitle2, (18, 194), bottomTitle2)
    block.paste(bottomNotation, (23, 117), bottomNotation)

    return block
