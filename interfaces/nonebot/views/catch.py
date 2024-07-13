import io
from typing import Any, TypeVar

import PIL
import PIL.Image
import PIL.ImageChops
import PIL.ImageDraw
from imagetext_py import TextAlign
from loguru import logger
from nonebot_plugin_alconna import UniMessage

from src.common.decorators.threading import make_async
from src.common.draw.texts import Fonts
from src.common.draw.tools import hex_to_rgb, imageToBytes, mix_color, rgb_to_hex
from src.views.catch import AwardDetail, CatchMesssage, CatchResultMessage, DisplayBox

from .basics import (
    apply_mask,
    draw_rounded_rectangle,
    paste_image,
    render_text,
    rounded_rectangle_mask,
    vertical_pile,
)

T = TypeVar("T")

DISPLAY_BOX_CACHE: dict[str, PIL.Image.Image] = {}


def _display_box(color: str, central_image: str | bytes) -> PIL.Image.Image:
    if not isinstance(central_image, str):
        image = PIL.Image.open(io.BytesIO(central_image)).convert("RGBA")
    else:
        image = PIL.Image.open(central_image).convert("RGBA")
        logger.info(f"图片 {central_image} 还没有被预渲染过，现在渲染。")
    image = image.resize((180, 144), PIL.Image.ADAPTIVE)
    image = apply_mask(image, rounded_rectangle_mask(180, 144, 10))

    canvas = PIL.Image.new("RGBA", (180, 144), (255, 255, 255, 0))

    outerRect = draw_rounded_rectangle(
        180, 144, 10, rgb_to_hex(mix_color(hex_to_rgb(color), (255, 255, 255), 0.35))
    )
    innerRect = draw_rounded_rectangle(176, 140, 8, color)

    paste_image(canvas, outerRect, 0, 0)
    paste_image(canvas, innerRect, 2, 2)
    paste_image(canvas, image, 0, 0)

    return canvas


def display_box(data: DisplayBox) -> PIL.Image.Image:
    """
    渲染 DisplayBox
    """

    cache_key = f"{data.color}-{hash(data.image)}"
    if cache_key not in DISPLAY_BOX_CACHE:
        DISPLAY_BOX_CACHE[cache_key] = _display_box(data.color, data.image)
    image = DISPLAY_BOX_CACHE[cache_key].copy()
    if data.new:
        image_new = PIL.Image.open("./res/new.png").convert("RGBA")
        paste_image(image, image_new, 88, 0)
    return image


def catch(data: AwardDetail) -> PIL.Image.Image:
    """
    渲染 AwardDetail
    """

    left_display = display_box(
        DisplayBox(color=data.color, image=data.image, new=data.new)
    )
    rightDescription = render_text(
        text=data.description,
        width=567,
        color="#ffffff",
        font=[Fonts.VONWAON_BITMAP_16, Fonts.MAPLE_UI],
        font_size=16,
        line_spacing=1.25,
        paragraph_spacing=15,
    )
    rightTitle = render_text(
        text=data.title,
        font_size=43,
        color="#ffffff",
        font=Fonts.JINGNAN_JUNJUN,
    )
    rightStar = render_text(
        text=data.stars,
        width=400,
        font_size=43,
        align=TextAlign.Right,
        color=data.color,
        font=Fonts.MAPLE_UI,
    )
    leftNotation = render_text(
        text=data.notation,
        color=(
            "#FFFFFF"
            if data.notation == "+1"
            else "#FFFD55" if data.notation == "+2" else "#8BFA84"
        ),
        font=Fonts.MARU_MONICA,
        font_size=48,
        margin_bottom=5,
        margin_top=0,
        margin_left=0,
    )
    leftNotationShadow = render_text(
        text=data.notation,
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
    paste_image(block, left_display, 18, 18)
    paste_image(block, rightTitle, 212, 18)
    paste_image(block, rightDescription, 212, 75)
    paste_image(block, rightStar, 379, 14)
    paste_image(block, leftNotationShadow, 26, 107)
    paste_image(block, leftNotation, 26, 107)

    return block


def render_catch_result_image(data: CatchResultMessage) -> PIL.Image.Image:
    """
    渲染 CatchResultMessage 的图片部分
    """

    docs: list[PIL.Image.Image] = []
    boxes: list[PIL.Image.Image] = []
    docs.append(
        render_text(
            text=data.title,
            color="#63605C",
            font=Fonts.JINGNAN_BOBO_HEI,
            font_size=96,
            width=800,
        )
    )
    docs.append(
        render_text(
            text=data.details,
            width=800,
            color="#9B9690",
            font=Fonts.ALIMAMA_SHU_HEI,
            font_size=28,
        )
    )
    for c in data.catchs:
        boxes.append(catch(c))
    docs_render = vertical_pile(docs)
    boxes_render = vertical_pile(boxes, 30)
    return vertical_pile(
        [docs_render, boxes_render],
        30,
        background="#EEEBE3",
        marginTop=60,
        marginBottom=80,
        marginLeft=80,
        marginRight=80,
    )


async def render_catch_result_mesage(data: CatchResultMessage) -> UniMessage[Any]:
    return UniMessage.image(
        raw=await make_async(imageToBytes)(
            await make_async(render_catch_result_image)(data)
        )
    )


async def render_catch_failed_message(data: CatchMesssage) -> UniMessage[Any]:
    return UniMessage.text(f"小哥还没长成，请再等{data.timedelta_text}吧！")
