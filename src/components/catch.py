from pathlib import Path

import PIL
import PIL.Image
from typing_extensions import deprecated

from interfaces.nonebot.views.catch import catch as _catch
from src.common.decorators.threading import make_async
from src.models.statics import Level
from src.views.award import AwardInfo


@deprecated("未来将会直接使用 interfaces.nonebot 中的 catch 函数")
async def catch(
    title: str,
    description: str,
    image: str | bytes | Path,
    stars: str,
    color: str,
    new: bool,
    notation: str,
) -> PIL.Image.Image:
    """在 Figma 中声明的抓到小哥的一个条目的对象

    Args:
        title (str): 一个小哥
        description (str): 小哥的描述
        image (str): 小哥的图片
        stars (str): 小哥星级的标注
        color (str): 星级的颜色，同时作为图片的背景色
        new (bool): 是否是新小哥，效果是在右上角显示一个 NEW
        notation (str): 小哥的名字左下角要显示什么批注文本

    Returns:
        PIL.Image.Image: 图片
    """

    return await make_async(_catch)(
        AwardInfo(
            aid=0,
            name=title,
            description=description,
            level=Level(
                display_name=stars,
                search_names=[],
                color=color,
                awarding=0,
                weight=0,
            ),
            image=image,
            sid=-1,
            skin_name=None,
            new=new,
            notation=notation,
        )
    )
