from imagetext_py import (
    Canvas,
    Color,
    Font,
    FontDB,
    Paint,
    TextAlign,
    WrapStyle,
    draw_text_multiline,
    draw_text_wrapped,
    text_size,
    text_size_multiline,
    text_wrap,
)

from src.common.decorators.threading import make_async
from src.common.draw.texts import Fonts


for font in Fonts:
    FontDB.LoadFromPath(font.name, font.value)


@make_async
def getTextImage(
    *,
    text: str,
    fontSize: float,
    font: Font | Fonts | str | list[Fonts],
    color: Paint | str,
    width: int | None = None,
    line_spacing: float = 1,
    align: TextAlign = TextAlign.Left,
    stroke: float | None = None,
    stroke_color: Paint | str | None = None,
    wrap_style: WrapStyle = WrapStyle.Character,
    marginLeft: float = 0,
    marginRight: float = 0,
    marginTop: float = 0,
    marginBottom: float = 0,
    drawEmoji: bool = True,
):
    # 先预处理一些量，这些量需要同时适配旧接口
    if isinstance(font, Fonts):
        font = FontDB.Query(font.name)
    elif isinstance(font, list):
        font = FontDB.Query(" ".join((f.name for f in font)))
    elif isinstance(font, str):
        font = FontDB.Query(font)

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
        lines = text_wrap(text, width, fontSize, font, drawEmoji, wrap_style)
        _width, _height = text_size_multiline(lines, fontSize, font, line_spacing, drawEmoji)
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
        canvas,
        lines,
        x,
        marginTop,
        ax,
        0.0,
        _width + marginRight,
        fontSize,
        font,
        color,
        line_spacing,
        align,
        stroke,
        stroke_color,
        drawEmoji,
    )

    return canvas.to_image()
