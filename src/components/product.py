import PIL
import PIL.Image
from imagetext_py import TextAlign

from src.common.dataclasses.shop_data import ProductData
from src.common.draw.texts import Fonts, getTextImage
from src.common.lang.zh import la
from src.components.display_box import display_box


async def product_box(product: ProductData):
    display = await display_box(product.background_color, product.image, False)
    title = await getTextImage(
        text=product.title,
        width=180,
        align=TextAlign.Center,
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        fontSize=26,
    )
    title2 = await getTextImage(
        text=product.description,
        width=180,
        color="#C4BEBD",
        font=Fonts.HARMONYOS_SANS_BLACK,
        fontSize=20,
        align=TextAlign.Center,
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

        notationBox = await getTextImage(
            text=notation,
            width=170,
            color="#FFFFFF",
            font=Fonts.MARU_MONICA,
            fontSize=36,
            stroke=4,
            marginBottom=5,
            marginLeft=5,
        )
        block.paste(notationBox, (26, 117), notationBox)

    return block
