import enum
import os
from typing import Iterable

import PIL
import PIL.Image
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
    JINGNAN_BOBO_HEI = _res("荆南波波黑-Bold.ttf") # 界面标题
    JINGNAN_JUNJUN = _res("JUNJUN.otf") # 界面次级标题
    ALIMAMA_SHU_HEI = _res("AlimamaShuHeiTi-Bold.ttf") # 界面小文字
    MAPLE_UI = _res("Maple UI.ttf")
    HARMONYOS_SANS_BLACK = _res("HarmonyOS_Sans_SC_Black.ttf")
    VONWAON_BITMAP_12 = _res("VonwaonBitmap-12px.ttf")
    VONWAON_BITMAP_16 = _res("VonwaonBitmap-16px.ttf")
    MARU_MONICA = _res("莫妮卡像素圆体 x12y16pxMaruMonica.otf")


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
    """获取一段文本的图像，图像的大小会随着文本占的空间变化

    Args:
        text (str): 输入的文本
        fontSize (float): 字体大小
        font (Font | Fonts | str | Iterable[Fonts]): 字体文件，最好从 Fonts 枚举中获得。可以输入一个 Fonts 元组或列表，以支持字体 Fallback。
        color (Paint | str): 颜色，使用井号开头的十六进制色号，或者使用 imagetext_py 中的 Paint 对象。
        width (int | None, optional): 文本框的宽度。如果不设定，文本会尽可能地长，而如果设定了，则会在宽度范围之内断行。
        line_spacing (float, optional): 行间距，默认是一倍行间距。
        align (TextAlign, optional): 字体对齐，请使用 TextAlign 枚举类。
        stroke (float, optional): 描边宽度。
        stroke_color (Paint | str, optional): 描边颜色。
        wrap_style (WrapStyle, optional): 断行方式，默认是 WrapStyle.Character。不知道为什么，感觉两个选项之间好像没有影响？
        marginLeft (float, optional): 字体框左边扩展的像素大小。
        marginRight (float, optional): 字体框右边扩展的像素大小。
        marginTop (float, optional): 字体框上面扩展的像素大小。
        marginBottom (float, optional): 字体框下面扩展的像素大小。
        drawEmoji (bool, optional): 是否绘制 Emoji 图像。
        scalar (float, optional): 绘制时使用的抗锯齿缩放倍数。

    Returns:
        PIL.Image.Image: PIL 库的 Image 对象
    """

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
    if img.width <= 0 or img.height <= 0:
        return PIL.Image.new("RGBA", (1, 1), "#00000000")
    
    return img.resize(
        (
            int(img.width / scalar),
            int(img.height / scalar),
        )
    )


__all__ = ["Fonts", "getTextImage", "TextAlign"]
