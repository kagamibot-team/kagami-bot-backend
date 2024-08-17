from typing import Any, TypeVar

from nonebot_plugin_alconna import UniMessage

from src.ui.base.browser import get_browser_pool
from src.ui.base.tools import image_to_bytes
from src.ui.components.catch import catch
from src.ui.views.award import AwardDisplay
from src.ui.views.catch import CatchMesssage, CatchResultMessage, SuccessfulCatch
from utils.threading import make_async

T = TypeVar("T")


async def render_catch_result_message(data: CatchResultMessage) -> UniMessage[Any]:
    return UniMessage.image(
        raw=await get_browser_pool().render(
            "zhua", SuccessfulCatch.from_catch_result(data)
        )
    )


async def render_catch_failed_message(data: CatchMesssage) -> UniMessage[Any]:
    return UniMessage.at(data.user.qqid).text(
        f" 小哥还没长成，请再等{data.timedelta_text}吧！"
    )


async def render_award_info_message(data: AwardDisplay) -> UniMessage[Any]:
    image = await make_async(catch)(data)
    return UniMessage.image(raw=await make_async(image_to_bytes)(image))


async def render_catch_message(message: CatchMesssage) -> UniMessage[Any]:
    if isinstance(message, CatchResultMessage):
        return await render_catch_result_message(message)
    return await render_catch_failed_message(message)
