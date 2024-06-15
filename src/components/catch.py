import PIL
import PIL.Image


from src.common.draw.texts import Fonts, drawASingleLineClassic, drawLimitedBoxOfTextClassic, drawLimitedBoxOfTextWithScalar
from src.common.draw.typing import Image
from src.components.display_box import display_box


async def catch(
    title: str,
    description: str,
    image: str,
    stars: str,
    color: str,
    new: bool,
    notation: str,
) -> Image:
    left_display = await display_box(color, image, new)
    rightDescription = await drawLimitedBoxOfTextClassic(
        text=description,
        maxWidth=567,
        lineHeight=19,
        color="#ffffff",
        font=Fonts.VONWAON_BITMAP_16,
        fontSize=16,
    )
    rightTitle = await drawASingleLineClassic(
        text=title,
        fontSize=43,
        color="#ffffff",
        font=Fonts.HARMONYOS_SANS_BLACK,
    )
    rightStar = await drawLimitedBoxOfTextWithScalar(
        stars,
        400,
        "right",
        "right",
        43,
        color,
        Fonts.HARMONYOS_SANS,
        28,
    )
    leftNotation = await drawASingleLineClassic(
        text=notation,
        color="#FFFFFF",
        font=Fonts.MARU_MONICA,
        fontSize=48,
        expandBottom=5,
        expandTop=0,
        expandLeft=0,
    )
    leftNotationShadow = await drawASingleLineClassic(
        text=notation,
        color="#000000",
        font=Fonts.MARU_MONICA,
        fontSize=48,
        expandBottom=5,
        expandTop=3,
        expandLeft=3,
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
