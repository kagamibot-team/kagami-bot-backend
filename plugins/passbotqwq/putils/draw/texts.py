from dataclasses import dataclass
import enum
import os
from typing import Literal

import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from ..threading import make_async

from .images import addUponPaste, newImage


class HorizontalAnchor(enum.Enum):
    left = "l"
    middle = "m"
    right = "r"
    baseline = "s"


class VerticalAnchor(enum.Enum):
    ascender = "a"
    top = "t"
    middle = "m"
    baseline = "s"
    bottom = "b"
    descender = "d"


@dataclass
class TextBox:
    left: int
    top: int
    right: int
    bottom: int


FONT_BASE = os.path.join(".", "res", "catch", "fonts")


def _res(fn: str):
    return os.path.join(FONT_BASE, fn)


class Fonts(enum.Enum):
    FONT_HARMONYOS_SANS = _res("HarmonyOS_Sans_SC_Regular.ttf")
    FONT_HARMONYOS_SANS_BLACK = _res("HarmonyOS_Sans_SC_Black.ttf")
    FONT_HARMONYOS_SANS_THIN = _res("HARMONYOS_SANS_SC_THIN.TTF")
    ALIMAMA_SHU_HEI = _res("AlimamaShuHeiTi-Bold.ttf")
    JINGNAN_BOBO_HEI = _res("荆南波波黑-Bold.ttf")
    JIANGCHENG_YUANTI = _res("江城圆体 500W.ttf")
    SUPERMERCADO = _res("SupermercadoOne-Regular.ttf")


def textFont(fontEnum: Fonts, fontSize: int):
    return PIL.ImageFont.FreeTypeFont(fontEnum.value, fontSize)


DEFAULT_FONT = textFont(Fonts.FONT_HARMONYOS_SANS, 12)


@make_async
def drawText(
    draw: PIL.ImageDraw.ImageDraw,
    text: str,
    x: float,
    y: float,
    color: str,
    font=DEFAULT_FONT,
    strokeColor: str = "#000000",
    strokeWidth: int = 0,
    horizontalAlign: HorizontalAnchor = HorizontalAnchor.left,
    verticalAlign: VerticalAnchor = VerticalAnchor.top,
):
    draw.text(
        (x, y),
        text,
        fill=color,
        font=font,
        stroke_fill=strokeColor,
        stroke_width=strokeWidth,
        anchor=horizontalAlign.value + verticalAlign.value,
    )


def getBoxOfText(text: str, font: PIL.ImageFont.FreeTypeFont = DEFAULT_FONT):
    left, top, right, bottom = font.getbbox(text)

    return TextBox(left, top, right, bottom)


async def drawABoxOfText(
    text: str,
    color: str,
    font=DEFAULT_FONT,
    strokeColor: str = "#000000",
    strokeWidth: int = 0,
    background: str = "#FFFFFF",
    marginLeft: int = 0,
    marginRight: int = 0,
    marginTop: int = 0,
    marginBottom: int = 0,
):
    box = getBoxOfText(text, font)
    image = await newImage(
        (
            box.right + marginLeft + marginRight,
            box.bottom + marginTop + marginBottom,
        ),
        background,
    )
    await drawText(
        PIL.ImageDraw.Draw(image),
        text,
        box.left + marginLeft,
        box.top + marginTop,
        color,
        font,
        strokeColor,
        strokeWidth,
    )

    return image


async def drawSingleLine(
    text: str,
    maxWidth: int,
    color: str,
    align: Literal["left", "right", "center", "expand"],
    font=DEFAULT_FONT,
    expandTop: int = 0,
    expandBottom: int = 0,
    expandLeft: int = 0,
    expandRight: int = 0,
    strokeWidth: int = 0,
    strokeColor: str = "#000000",
):
    boxes = [getBoxOfText(t, font) for t in text]

    base = PIL.Image.new(
        "RGBA",
        (
            expandLeft + expandRight + maxWidth,
            expandTop + expandBottom + max([e.bottom for e in boxes]),
        ),
        "#00000000",
    )
    draw = PIL.ImageDraw.Draw(base)

    space = maxWidth - sum([e.right for e in boxes])

    if align == "left" or align == "expand":
        leftPointer = expandLeft
    elif align == "right":
        leftPointer = space + expandLeft
    elif align == "center":
        leftPointer = space / 2 + expandLeft

    for i, t in enumerate(text):
        box = boxes[i]
        await drawText(
            draw,
            t,
            box.left + leftPointer,
            box.top + expandTop,
            color,
            font,
            strokeColor,
            strokeWidth,
        )

        if align == "expand":
            leftPointer += space / (len(text) - 1)

        leftPointer += box.right

    return base


async def drawLimitedBoxOfText(
    text: str,
    maxWidth: int,
    align: Literal["left", "right", "center", "expand"],
    alignLastLine: Literal["left", "right", "center", "expand"],
    lineHeight: int,
    color: str = "#000000",
    font: Fonts = Fonts.FONT_HARMONYOS_SANS,
    fontSize: int = 16,
    expandTop: int = 0,
    expandBottom: int = 0,
    expandLeft: int = 0,
    expandRight: int = 0,
    expandInnerTop: int = 0,
    expandInnerBottom: int = 0,
    expandInnerLeft: int = 0,
    expandInnerRight: int = 0,
    strokeWidth: int = 0,
    strokeColor: str = "#000000",
):
    lines: list[str] = []
    lWidth = 0
    lCache = ""

    for t in text:
        if t == '\n':
            lines.append(lCache)
            lCache = ""
            continue

        box = getBoxOfText(t, textFont(font, fontSize))
        if box.right + lWidth > maxWidth:
            lWidth = box.right
            lines.append(lCache)
            lCache = t
        else:
            lCache += t
            lWidth += box.right
    
    if lCache:
        lines.append(lCache)

    base = PIL.Image.new(
        "RGBA",
        (
            expandLeft + expandRight + maxWidth,
            expandTop + expandBottom + (len(lines) + 1) * lineHeight,
        ),
        "#00000000",
    )

    leftPointer = expandLeft
    topPointer = expandTop

    for ind, line in enumerate(lines):
        await addUponPaste(
            base,
            await drawSingleLine(
                line,
                maxWidth,
                color,
                align if ind + 1 != len(lines) else alignLastLine,
                textFont(font, fontSize),
                expandInnerTop,
                expandInnerBottom,
                expandInnerLeft,
                expandInnerRight,
                strokeWidth,
                strokeColor,
            ),
            -expandInnerLeft + leftPointer,
            -expandInnerTop + topPointer,
        )
        topPointer += lineHeight
    return base


async def drawLimitedBoxOfTextWithScalar(
    text: str,
    maxWidth: int,
    align: Literal["left", "right", "center", "expand"],
    alignLastLine: Literal["left", "right", "center", "expand"],
    lineHeight: int,
    color: str = "#000000",
    font: Fonts = Fonts.FONT_HARMONYOS_SANS,
    fontSize: int = 16,
    expandTop: int = 0,
    expandBottom: int = 0,
    expandLeft: int = 0,
    expandRight: int = 0,
    expandInnerTop: int = 0,
    expandInnerBottom: int = 0,
    expandInnerLeft: int = 0,
    expandInnerRight: int = 0,
    strokeWidth: int = 0,
    strokeColor: str = "#000000",
    scalar: int = 3,
):
    res = await drawLimitedBoxOfText(
        text,
        maxWidth * scalar,
        align,
        alignLastLine,
        lineHeight * scalar,
        color,
        font,
        fontSize * scalar,
        expandTop * scalar,
        expandBottom * scalar,
        expandLeft * scalar,
        expandRight * scalar,
        expandInnerTop * scalar,
        expandInnerBottom * scalar,
        expandInnerLeft * scalar,
        expandInnerRight * scalar,
        strokeWidth * scalar,
        strokeColor,
    )

    towardsSize = (
        res.width // scalar,
        res.height // scalar,
    )

    return res.resize(towardsSize, resample=PIL.Image.Resampling.LANCZOS)
