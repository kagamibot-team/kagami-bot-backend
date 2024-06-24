import PIL
import PIL.Image
from imagetext_py import TextAlign


from src.common.draw.texts import Fonts
from src.common.draw.textv2 import getTextImage
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
        font=Fonts.VONWAON_BITMAP_16,
        fontSize=16,
    )
    rightTitle = await getTextImage(
        text=title,
        fontSize=43,
        color="#ffffff",
        font=Fonts.HARMONYOS_SANS_BLACK,
    )
    rightStar = await getTextImage(
        text=stars,
        width=400,
        fontSize=43,
        align=TextAlign.Right,
        color=color,
        font=Fonts.HARMONYOS_SANS,
    )
    leftNotation = await getTextImage(
        text=notation,
        color="#FFFFFF",
        font=Fonts.MARU_MONICA,
        fontSize=48,
        marginBottom=5,
        marginTop=0,
        marginLeft=0,
    )
    leftNotationShadow = await getTextImage(
        text=notation,
        color="#000000",
        font=Fonts.MARU_MONICA,
        fontSize=48,
        marginBottom=5,
        marginTop=3,
        marginLeft=3,
    )

    block = PIL.Image.new(
        "RGB", (800, max(180, rightDescription.height + 89)), "#9B9690"
    )
    block.paste(left_display, (18, 18), left_display)
    block.paste(rightTitle, (212, 18), rightTitle)
    block.paste(rightDescription, (212, 75), rightDescription)
    block.paste(rightStar, (379, 18), rightStar)
    block.paste(leftNotationShadow, (26, 107), leftNotationShadow)
    block.paste(leftNotation, (26, 107), leftNotation)

    return block
