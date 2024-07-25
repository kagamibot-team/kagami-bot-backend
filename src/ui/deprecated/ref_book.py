import PIL
import PIL.Image
from imagetext_py import TextAlign

from src.ui.base.basics import Fonts, paste_image, render_text
from src.ui.deprecated.display_box import display_box


async def __title(text: str, color: str = "#FFFFFF"):
    return render_text(
        text=text,
        width=180,
        color=color,
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=24,
        align=TextAlign.Center,
    )


async def skin_book(title: str, title2: str, notation: str, color: str, imgUrl: str):
    box = await display_box(color, imgUrl)

    bottomTitle = await __title(title)
    bottomTitle2 = await __title(title2, "#C4BEBD")

    bottomNotation = render_text(
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
    paste_image(block, box, 18, 18)
    paste_image(block, bottomTitle, 18, 170)
    paste_image(block, bottomTitle2, 18, 194)
    paste_image(block, bottomNotation, 23, 117)

    return block
