from dataclasses import dataclass
import enum

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


class Fonts(enum.Enum):
    FONT_HARMONYOS_SANS = r"C:\Windows\Fonts\HarmonyOS_Sans_SC_Regular.ttf"
    FONT_HARMONYOS_SANS_BLACK = r"C:\Windows\Fonts\HarmonyOS_Sans_SC_Black.ttf"
    ALIMAMA_SHU_HEI = r"F:\AlimamaShuHeiTi-Bold.ttf"
    JINGNAN_BOBO_HEI = r"c:\Users\Passt\AppData\Local\Microsoft\Windows\Fonts\荆南波波黑-Bold.ttf"
    JIANGCHENG_YUANTI = r"C:\Windows\Fonts\江城圆体 500W.ttf"


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
