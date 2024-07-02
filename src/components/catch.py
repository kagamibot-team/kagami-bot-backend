import PIL
import PIL.Image
from imagetext_py import TextAlign


from src.common.draw.images import imagePaste
from src.common.draw.texts import Fonts, getTextImage
from src.components.display_box import display_box


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
    rightDescription = await getTextImage(
        text=description,
        width=567,
        color="#ffffff",
        font=[Fonts.VONWAON_BITMAP_16, Fonts.MAPLE_UI],
        font_size=16,
    )
    rightTitle = await getTextImage(
        text=title,
        font_size=43,
        color="#ffffff",
        font=Fonts.JINGNAN_JUNJUN,
    )
    rightStar = await getTextImage(
        text=stars,
        width=400,
        font_size=43,
        align=TextAlign.Right,
        color=color,
        font=Fonts.MAPLE_UI,
    )
    leftNotation = await getTextImage(
        text=notation,
        color="#FFFFFF",
        font=Fonts.MARU_MONICA,
        font_size=48,
        margin_bottom=5,
        margin_top=0,
        margin_left=0,
    )
    leftNotationShadow = await getTextImage(
        text=notation,
        color="#000000",
        font=Fonts.MARU_MONICA,
        font_size=48,
        margin_bottom=5,
        margin_top=3,
        margin_left=3,
    )

    block = PIL.Image.new(
        "RGB", (800, max(180, rightDescription.height + 89)), "#9B9690"
    )
    await imagePaste(block, left_display, 18, 18)
    await imagePaste(block, rightTitle, 212, 18)
    await imagePaste(block, rightDescription, 212, 75)
    await imagePaste(block, rightStar, 379, 14)
    await imagePaste(block, leftNotationShadow, 26, 107)
    await imagePaste(block, leftNotation, 26, 107)

    return block
