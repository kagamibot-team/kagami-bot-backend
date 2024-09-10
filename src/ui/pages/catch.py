from typing import Any, TypeVar

from nonebot_plugin_alconna import UniMessage

from src.ui.base.browser import get_browser_pool
from src.ui.types.common import DisplayAward
from src.ui.types.zhua import ZhuaData
from src.ui.views.award import AwardDisplay

T = TypeVar("T")


async def render_catch_failed_message(data: ZhuaData) -> UniMessage[Any]:
    return UniMessage.at(data.user.qqid).text(
        f" 小哥还没长成，请再等{data.meta.need_time}吧！"
    )


async def render_award_info_message(
    data: AwardDisplay, count: int | None = None, stats: int | None = None
) -> UniMessage[Any]:
    if count is None:
        count = -1
    stats_val = str(stats or "")
    image = await get_browser_pool().render(
        "catch",
        DisplayAward(info=data.info, count=count, is_new=False, stats=stats_val),
    )
    return UniMessage.image(raw=image)


async def render_catch_message(data: ZhuaData) -> UniMessage[Any]:
    if len(data.catchs) > 0:
        return UniMessage.image(raw=await get_browser_pool().render("zhua", data))
    return await render_catch_failed_message(data)
