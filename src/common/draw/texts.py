import enum
import os
from typing import Iterable

from imagetext_py import (
    Canvas,
    Color,
    Font,
    FontDB,
    Paint,
    TextAlign,
    WrapStyle,
    draw_text_multiline,
    text_size,
    text_size_multiline,
    text_wrap,
)

from src.common.decorators.threading import make_async


FONT_BASE = os.path.join(".", "res", "fonts")


def _res(fn: str):
    return os.path.join(FONT_BASE, fn)


class Fonts(enum.Enum):
    MAPLE_UI = _res("Maple UI.ttf")
    HARMONYOS_SANS_BLACK = _res("HarmonyOS_Sans_SC_Black.ttf")
    ALIMAMA_SHU_HEI = _res("AlimamaShuHeiTi-Bold.ttf")
    JINGNAN_BOBO_HEI = _res("荆南波波黑-Bold.ttf")
    VONWAON_BITMAP_12 = _res("VonwaonBitmap-12px.ttf")
    VONWAON_BITMAP_16 = _res("VonwaonBitmap-16px.ttf")
    MARU_MONICA = _res("莫妮卡像素圆体 x12y16pxMaruMonica.otf")
    JINGNAN_JUNJUN = _res("JUNJUN.otf")


for font in Fonts:
    FontDB.LoadFromPath(font.name, font.value)


@make_async
def getTextImage(
    *,
    text: str,
    fontSize: float,
    font: Font | Fonts | str | Iterable[Fonts],
    color: Paint | str,
    width: int | None = None,
    line_spacing: float = 1,
    align: TextAlign = TextAlign.Left,
    stroke: float = 0.0,
    stroke_color: Paint | str = "#00000000",
    wrap_style: WrapStyle = WrapStyle.Character,
    marginLeft: float = 0,
    marginRight: float = 0,
    marginTop: float = 0,
    marginBottom: float = 0,
    drawEmoji: bool = True,
    scalar: float = 2,
):
    # 最开始，先处理一些抗锯齿缩放的问题
    marginLeft *= scalar
    marginRight *= scalar
    marginTop *= scalar
    marginBottom *= scalar
    stroke *= scalar
    fontSize *= scalar

    # 先预处理一些量，这些量需要同时适配旧接口
    if isinstance(font, Fonts):
        font = FontDB.Query(font.name)
    elif isinstance(font, str):
        font = FontDB.Query(font)
    elif isinstance(font, Iterable):
        font = FontDB.Query(" ".join((f.name for f in font)))

    if isinstance(color, str):
        color = Paint.Color(Color.from_hex(color[1:]))

    if isinstance(stroke_color, str):
        stroke_color = Paint.Color(Color.from_hex(stroke_color[1:]))

    if width is None:
        # 这种情况表示绘制单行文本
        lines = [text]
        _width, _height = text_size(text, fontSize, font, drawEmoji)
    else:
        # 这种情况就是多行文本了
        width = int(width * scalar)

        lines = text_wrap(text, width, fontSize, font, drawEmoji, wrap_style)
        _width, _height = text_size_multiline(
            lines, fontSize, font, line_spacing, drawEmoji
        )
        _width = width

    canvas = Canvas(
        int(_width + marginLeft + marginRight),
        int(_height + marginTop + marginBottom),
        Color(0, 0, 0, 0),
    )

    if align == TextAlign.Left:
        ax = 0.0
        x = marginLeft
    elif align == TextAlign.Right:
        ax = 1.0
        x = marginLeft + _width
    else:
        ax = 0.5
        x = marginLeft + _width / 2

    draw_text_multiline(
        canvas=canvas,
        lines=lines,
        x=x,
        y=marginTop,
        ax=ax,
        ay=0.0,
        width=_width + marginRight,
        size=fontSize,
        font=font,
        fill=color,
        line_spacing=line_spacing,
        align=align,
        stroke=stroke,
        stroke_color=stroke_color,
        draw_emojis=drawEmoji,
    )

    img = canvas.to_image()
    return img.resize(
        (
            int(img.width / scalar),
            int(img.height / scalar),
        )
    )


__all__ = ["Fonts", "getTextImage", "TextAlign"]
