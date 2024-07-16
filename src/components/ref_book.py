import PIL
import PIL.Image
from imagetext_py import TextAlign

from src.common.draw.images import imagePaste
from src.common.draw.texts import Fonts, getTextImage
from src.components.display_box import display_box


async def __title(text: str, color: str = "#FFFFFF"):
    return await getTextImage(
        text=text,
        width=180,
        color=color,
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=24,
        align=TextAlign.Center,
    )


async def ref_book_box(
    title: str, notationSto: str, notationSta: str, color: str, imgUrl: str
):
    box = await display_box(color, imgUrl)

    bottomTitle = await __title(title)

    bottomLeftNotation = await getTextImage(
        text=notationSto,
        width=170,
        color="#FFFFFF",
        font=Fonts.MARU_MONICA,
        font_size=48,
        stroke=2,
        stroke_color="#000000",
        margin_bottom=5,
        margin_left=5,
    )

    topLeftNotation = await getTextImage(
        text=notationSta,
        width=170,
        color="#000000",
        font=Fonts.MARU_MONICA,
        font_size=48,
        stroke=2,
        stroke_color="#FFFFFF",
        margin_bottom=5,
        margin_left=5,
    )

    block = PIL.Image.new("RGB", (216, 210), "#9B9690")
    await imagePaste(block, box, 18, 18)
    await imagePaste(block, bottomTitle, 18, 170)
    await imagePaste(block, bottomLeftNotation, 23, 105)
    await imagePaste(block, topLeftNotation, 23, 23)

    return block


async def skin_book(title: str, title2: str, notation: str, color: str, imgUrl: str):
    box = await display_box(color, imgUrl)

    bottomTitle = await __title(title)
    bottomTitle2 = await __title(title2, "#C4BEBD")

    bottomNotation = await getTextImage(
        text=notation,
        width=170,
        color="#FFFFFF",
        font=Fonts.MARU_MONICA,
        font_size=36,
        stroke=2,
        stroke_color="#000000",
        margin_bottom=5,
        margin_left=5,
    )

    block = PIL.Image.new("RGB", (216, 234), "#9B9690")
    await imagePaste(block, box, 18, 18)
    await imagePaste(block, bottomTitle, 18, 170)
    await imagePaste(block, bottomTitle2, 18, 194)
    await imagePaste(block, bottomNotation, 23, 117)

    return block
