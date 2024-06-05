from dataclasses import dataclass
import enum
import os

import PIL
import PIL.ImageDraw
import PIL.ImageFont

from .typing import PILLOW_COLOR_LIKE_WEAK, IMAGE, PILLOW_COLOR_LIKE_STRONG


@dataclass
class TextBox:
    left: int
    top: int
    right: int
    bottom: int


FONT_BASE = os.path.join(os.getcwd(), 'res', 'catch', 'fonts')


def _res(fn: str):
    return os.path.join(FONT_BASE, fn)


class Fonts(enum.Enum):
    FONT_HARMONYOS_SANS = _res("HarmonyOS_Sans_SC_Regular.ttf")
    FONT_HARMONYOS_SANS_BLACK = _res("HarmonyOS_Sans_SC_Black.ttf")
    ALIMAMA_SHU_HEI = _res("AlimamaShuHeiTi-Bold.ttf")
    JINGNAN_BOBO_HEI = _res("荆南波波黑-Bold.ttf")
    JIANGCHENG_YUANTI = _res("江城圆体 500W.ttf")


def textFont(fontEnum: Fonts, fontSize: int):
    return PIL.ImageFont.FreeTypeFont(fontEnum.value, fontSize)


DEFAULT_FONT = textFont(Fonts.FONT_HARMONYOS_SANS, 12)


def drawText(
    draw: PIL.ImageDraw.ImageDraw,
    text: str,
    x: float,
    y: float,
    color: PILLOW_COLOR_LIKE_STRONG,
    font=DEFAULT_FONT,
    strokeColor: PILLOW_COLOR_LIKE_STRONG = 0,
    strokeWidth: int = 0
):
    draw.text((x, y), text, fill=color, font=font, stroke_fill=strokeColor, stroke_width=strokeWidth)


def textBox(text: str, font: PIL.ImageFont.FreeTypeFont = DEFAULT_FONT):
    left, top, right, bottom = font.getbbox(text)

    return TextBox(left, top, right, bottom)
