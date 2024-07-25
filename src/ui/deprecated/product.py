import PIL
import PIL.Image
from imagetext_py import TextAlign

from src.common.dataclasses.shop_data import ProductData
from src.common.lang.zh import la
from src.ui.base.basics import Fonts, paste_image, render_text
from src.ui.deprecated.display_box import display_box


async def product_box(product: ProductData):
    display = await display_box(product.background_color, product.image, False)
    title = render_text(
        text=product.title,
        width=180,
        align=TextAlign.Center,
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=26,
    )
    title2 = render_text(
        text=product.description,
        width=180,
        color="#C4BEBD",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=20,
        align=TextAlign.Center,
    )

    if product.sold_out:
        image_new = PIL.Image.open("./res/sold_out.png")
        image_new = image_new.convert("RGBA")

        paste_image(display, image_new, 0, 0)

    block = PIL.Image.new("RGB", (216, 234), "#9B9690")
    paste_image(block, display, 18, 18)
    paste_image(block, title, 18, 170)
    paste_image(block, title2, 18, 194)

    if not product.sold_out:
        notation = str(int(product.price)) + la.unit.money

        notationBox = render_text(
            text=notation,
            width=170,
            color="#FFFFFF",
            font=Fonts.MARU_MONICA,
            font_size=36,
            stroke=4,
            margin_bottom=5,
            margin_left=5,
        )
        notationBoxShadow = render_text(
            text=notation,
            width=170,
            color="#000000",
            font=Fonts.MARU_MONICA,
            font_size=36,
            stroke=4,
            margin_top=2,
            margin_bottom=5,
            margin_left=7,
        )
        paste_image(block, notationBoxShadow, 26, 117)
        paste_image(block, notationBox, 26, 117)

    return block
