import PIL
import PIL.Image
from src.common.dataclasses.shop_data import ProductData
from src.common.draw.texts import Fonts, HorizontalAnchor, drawLimitedBoxOfTextClassic, drawLimitedBoxOfTextWithScalar
from src.common.lang.zh import la
from src.components.display_box import display_box


async def product_box(product: ProductData):
    display = await display_box(product.background_color, product.image, False)
    title = await drawLimitedBoxOfTextWithScalar(
        product.title,
        180,
        "center",
        "center",
        24,
        "#FFFFFF",
        Fonts.HARMONYOS_SANS_BLACK,
        20,
        scalar=2,
    )
    title2 = await drawLimitedBoxOfTextWithScalar(
        product.description,
        180,
        "center",
        "center",
        24,
        "#C4BEBD",
        Fonts.HARMONYOS_SANS_BLACK,
        20,
        scalar=2,
    )

    if product.sold_out:
        image_new = PIL.Image.open("./res/sold_out.png")
        image_new = image_new.convert("RGBA")

        display.paste(image_new, (0, 0), image_new)

    block = PIL.Image.new("RGB", (216, 234), "#9B9690")
    block.paste(display, (18, 18), display)
    block.paste(title, (18, 170), title)
    block.paste(title2, (18, 194), title2)

    if not product.sold_out:
        notation = str(product.price) + la.unit.money
        
        notationBox = await drawLimitedBoxOfTextClassic(
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
        block.paste(notationBox, (26, 107), notationBox)

    return block
