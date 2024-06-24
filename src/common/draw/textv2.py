from imagetext_py import (
    Canvas,
    Color,
    Font,
    FontDB,
    Paint,
    TextAlign,
    WrapStyle,
    draw_text_wrapped,
)

from src.common.decorators.threading import make_async
from src.common.draw.texts import Fonts


for font in Fonts:
    FontDB.LoadFromPath(font.name, font.value)


@make_async
def getTextImage(
    *,
    text: str,
    width: int,
    height: int,
    fontSize: float,
    font: Font | Fonts,
    fill: Paint | str,
    x: float=0.0,
    y: float=0.0,
    anchorX: float=0.0,
    anchorY: float=0.0,
    line_spacing: float = 1,
    align: TextAlign = TextAlign.Left,
    stroke: float | None = None,
    stroke_color: Paint | str | None = None,
    draw_emojis: bool = False,
    wrap_style: WrapStyle = WrapStyle.Character
):
    canvas = Canvas(width, height, Color(0, 0, 0, 0))

    if isinstance(font, Fonts):
        font = FontDB.Query(font.name)

    if isinstance(fill, str):
        fill = Paint.Color(Color.from_hex(fill[1:]))

    if isinstance(stroke_color, str):
        stroke_color = Paint.Color(Color.from_hex(stroke_color[1:]))

    draw_text_wrapped(
        canvas=canvas,
        text=text,
        x=x,
        y=y,
        ax=anchorX,
        ay=anchorY,
        width=width,
        size=fontSize,
        font=font,
        fill=fill,
        line_spacing=line_spacing,
        align=align,
        stroke=stroke,
        stroke_color=stroke_color,
        draw_emojis=draw_emojis,
        wrap_style=wrap_style,
    )
    return canvas.to_image()
