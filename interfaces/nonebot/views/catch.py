from typing import Any, TypeVar

import PIL
import PIL.Image
import PIL.ImageChops
import PIL.ImageDraw
from imagetext_py import TextAlign
from nonebot_plugin_alconna import UniMessage

from src.common.decorators.threading import make_async
from src.common.draw.texts import Fonts
from src.common.draw.tools import imageToBytes
from src.views.award import AwardInfo
from src.views.catch import CatchMesssage, CatchResultMessage

from .awards import display_box
from .basics import paste_image, render_text, vertical_pile

T = TypeVar("T")


def catch(data: AwardInfo) -> PIL.Image.Image:
    """
    渲染 AwardDetail
    """

    left_display = display_box(data)
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
        text=data.display_name,
        font_size=43,
        color="#ffffff",
        font=Fonts.JINGNAN_JUNJUN,
    )
    rightStar = render_text(
        text=data.level.display_name,
        width=400,
        font_size=43,
        align=TextAlign.Right,
        color=data.level.color,
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


async def render_catch_result_message(data: CatchResultMessage) -> UniMessage[Any]:
    return UniMessage.image(
        raw=await make_async(imageToBytes)(
            await make_async(render_catch_result_image)(data)
        )
    )


async def render_catch_failed_message(data: CatchMesssage) -> UniMessage[Any]:
    return UniMessage.text(f"小哥还没长成，请再等{data.timedelta_text}吧！")


async def render_award_info_message(data: AwardInfo) -> UniMessage[Any]:
    image = await make_async(catch)(data)
    return UniMessage.image(raw=await make_async(imageToBytes)(image))


async def render_catch_message(message: CatchMesssage) -> UniMessage[Any]:
    if isinstance(message, CatchResultMessage):
        return await render_catch_result_message(message)
    return await render_catch_failed_message(message)
