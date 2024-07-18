from pathlib import Path

import PIL
import PIL.Image
from typing_extensions import deprecated

from interfaces.nonebot.components.awards import display_box as _display_box
from src.common.decorators.threading import make_async
from src.models.statics import Level
from src.views.award import AwardInfo


@deprecated("未来将会直接使用 interfaces.nonebot 中的 display_box 函数")
async def display_box(
    color: str, central_image: Path | str | bytes, new: bool = False
) -> PIL.Image.Image:
    return await make_async(_display_box)(
        AwardInfo(
            aid=-1,
            name="",
            description="",
            image=central_image,
            new=new,
            sid=0,
            skin_name="",
            notation="",
            level=Level(
                search_names=[],
                display_name="",
                weight=0,
                color=color,
                awarding=0,
                lid=0,
                sorting_priority=0,
            ),
        )
    )
