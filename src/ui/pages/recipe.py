from pathlib import Path
from typing import Any

import PIL
import PIL.Image
import PIL.ImageDraw
from imagetext_py import TextAlign
from nonebot_plugin_alconna import UniMessage

from src.ui.base.basics import (
    Fonts,
    horizontal_pile,
    paste_image,
    render_text,
    vertical_pile,
)
from src.ui.base.tools import image_to_bytes
from src.ui.components.awards import display_box
from src.ui.components.catch import catch
from src.ui.views.recipe import MergeResult
from utils.threading import make_async


def render_merge_image(data: MergeResult):
    ########
    # 前景 #
    ########
    area_title_1 = render_text(
        text=data.title1,
        font_size=80,
        font=Fonts.HARMONYOS_SANS_BLACK,
        color="#FFFFFF",
        width=1188,
        margin_left=50,
        margin_right=50,
    )

    area_title_2 = render_text(
        text=data.title2,
        font_size=60,
        font=Fonts.HARMONYOS_SANS_BLACK,
        width=567,
        color="#FFFFFF",
    )

    mats = [display_box(inp) for inp in data.inputs]
    area_material_box = vertical_pile(
        images=mats,
        paddingY=24,
        marginLeft=18,
        marginBottom=24,
    )

    area_product_entry = catch(data.output, background="#9B969099")

    area_title_3 = render_text(
        text=data.title3,
        width=567,
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=24,
        margin_top=12,
    )

    document = horizontal_pile(
        [
            PIL.Image.new("RGBA", (50, 1)),
            area_material_box,
            PIL.Image.new("RGBA", (100, 1)),
            vertical_pile(
                [
                    PIL.Image.new("RGBA", (1, 160)),
                    area_title_2,
                    PIL.Image.new("RGBA", (1, 30)),
                    area_product_entry,
                    PIL.Image.new("RGBA", (1, 30)),
                    area_title_3,
                ]
            ),
        ],
        align="top",
    )

    foreground = vertical_pile(
        [
            PIL.Image.new("RGBA", (1, 60)),
            area_title_1,
            PIL.Image.new("RGBA", (1, 120)),
            document,
            PIL.Image.new("RGBA", (1, 60)),
        ],
        background="#00000000",
    )

    ########
    # 背景 #
    ########

    msg = data.ymh_message

    background = PIL.Image.new("RGBA", foreground.size, "#8332D3")

    draw = PIL.ImageDraw.Draw(background)
    draw.ellipse((-1200, -1200, 1200, 1200), "#9149D8")
    draw.ellipse((-900, -900, 900, 900), "#9A56DD")
    draw.ellipse((-600, -600, 600, 600), "#9D5DDD")

    top0 = area_title_1.height - 78

    ymh = PIL.Image.open(msg.image.image_url)
    ratio = 0.25
    ymh = ymh.resize((int(ymh.width * ratio), int(ymh.height * ratio)))

    ymh_text = render_text(
        text=msg.text,
        font_size=48,
        font=Fonts.JINGNAN_BOBO_HEI,
        color="#333333",
        width=410,
        align=TextAlign.Center,
    )
    top = 190 + (180 - ymh_text.height) / 2 + top0

    paste_image(background, ymh, 550 + top0, 60)
    paste_image(
        background, PIL.Image.open(Path("./res/mokie/榆木华对话框.png")), 0, top0
    )
    paste_image(background, foreground, 0, 0)
    paste_image(background, ymh_text, 320, int(top))

    return background


async def render_merge_message(data: MergeResult) -> UniMessage[Any]:
    image = await make_async(image_to_bytes)(await make_async(render_merge_image)(data))

    return UniMessage.image(raw=image)
