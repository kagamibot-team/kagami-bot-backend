from typing import Any, TypeVar

import PIL
import PIL.Image
import PIL.ImageChops
import PIL.ImageDraw
from nonebot_plugin_alconna import UniMessage

from src.common.decorators.threading import make_async
from src.common.draw.texts import Fonts
from src.common.draw.tools import imageToBytes
from src.views.award import AwardInfo
from src.views.catch import CatchMesssage, CatchResultMessage

from ..base.basics import render_text, vertical_pile
from ..components.catch import catch

T = TypeVar("T")


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
