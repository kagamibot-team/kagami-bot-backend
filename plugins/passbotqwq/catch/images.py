import math
import time

import PIL
import PIL.ImageDraw

from plugins.passbotqwq.putils.threading import make_async
from .models import Award
from ..putils.draw.shapes import rectangle
from ..putils.draw.images import addUponPaste, loadImage, addUpon
from ..putils.draw.texts import drawText, textBox, textFont, Fonts
from ..putils.draw.typing import IMAGE
from ..putils.draw import newImage

from .data import (
    getAllAwardsOfOneUser,
    getAllLevels,
    getAllLevelsOfAwardList,
    getAwardCoundOfOneUser,
)


WIDTH = 2000
HEIGHT = 1600

STORAGE_MARGIN_LEFT = 30
STORAGE_MARGIN_RIGHT = 30
STORAGE_MARGIN_TOP = 70
STORAGE_MARGIN_BOTTOM = 20

STORAGE_BOX_PADDING_X = 5
STORAGE_BOX_PADDING_Y = 5
STORAGE_BOX_MARGIN_LEFT = 0
STORAGE_BOX_MARGIN_RIGHT = 0
STORAGE_BOX_MARGIN_TOP = -10
STORAGE_BOX_MARGIN_BOTTOM = 60

STORAGE_BOX_SCALE = 0.04

STORAGE_BOX_XCOUNT_MAX = 4

STORAGE_BACKGROUND_COLOR = "#696361"
STORAGE_BOX_COLOR = "#9e9d95"
STORAGE_TEXT_COLOR = "#FFFFFF"

STORAGE_TEXT_FONT = textFont(Fonts.JINGNAN_BOBO_HEI, 24)
STORAGE_COUNT_FONT = textFont(Fonts.FONT_HARMONYOS_SANS_BLACK, 18)
STORAGE_COUNT_COLOR = STORAGE_TEXT_COLOR
STORAGE_COUNT_STROKE_COLOR = "#000000"
STORAGE_COUNT_STROKE_WIDTH = 1

STORAGE_COUNT_DX = 2
STORAGE_COUNT_DY = -2

# 计算值
STORAGE_BOX_WIDTH = WIDTH * STORAGE_BOX_SCALE
STORAGE_BOX_HEIGHT = HEIGHT * STORAGE_BOX_SCALE

STORAGE_SPECIFIED_COLOR = {
    "壹": "#d1cccb",
    "贰": "#92d47b",
    "叁": "#89c2e8",
    "肆": "#d8adf7",
    "伍": "#facb4b",
}


def _get_width_of_boxes(count: int):
    return (
        STORAGE_BOX_MARGIN_LEFT
        + STORAGE_BOX_MARGIN_RIGHT
        + STORAGE_BOX_PADDING_X * (count - 1)
        + STORAGE_BOX_WIDTH * count
    )


def _get_height_of_boxes(lines: int):
    return (
        STORAGE_BOX_MARGIN_TOP
        + STORAGE_BOX_MARGIN_BOTTOM
        + STORAGE_BOX_PADDING_Y * (lines - 1)
        + STORAGE_BOX_HEIGHT * lines
    )


def drawStorageBlock(
    src: IMAGE, award: Award, count: int, x: float, y: float, size: float = 0.1
):
    rectangle(src, x, y, STORAGE_BOX_WIDTH, STORAGE_BOX_HEIGHT, STORAGE_BOX_COLOR)
    addUponPaste(
        src,
        loadImage(award.imgPath).resize(
            (
                int(STORAGE_BOX_WIDTH),
                int(STORAGE_BOX_HEIGHT),
            )
        ),
        int(x),
        int(y),
    )

    draw = PIL.ImageDraw.Draw(src)
    tbox = textBox(str(count), STORAGE_COUNT_FONT)

    drawText(
        draw,
        str(count),
        x + STORAGE_BOX_WIDTH + STORAGE_COUNT_DX,
        y + STORAGE_BOX_HEIGHT - tbox.bottom + STORAGE_COUNT_DY,
        STORAGE_COUNT_COLOR,
        STORAGE_COUNT_FONT,
        STORAGE_COUNT_STROKE_COLOR,
        STORAGE_COUNT_STROKE_WIDTH,
    )


@make_async
def drawStorage(uid: int):
    beginTime = time.time()
    boxes: list[tuple[float, float]] = []

    awards = getAllAwardsOfOneUser(uid)

    for level in getAllLevelsOfAwardList(getAllAwardsOfOneUser(uid)):
        tbox = textBox(f"稀有度为【{level.name}】的全部小哥", STORAGE_TEXT_FONT)
        boxes.append((tbox.right - tbox.left, tbox.bottom - tbox.top))

        awardsLength = len([a for a in awards if a.levelId == level.lid])

        if awardsLength >= STORAGE_BOX_XCOUNT_MAX:
            boxes.append(
                (
                    _get_width_of_boxes(STORAGE_BOX_XCOUNT_MAX),
                    _get_height_of_boxes(
                        math.ceil(awardsLength / STORAGE_BOX_XCOUNT_MAX)
                    ),
                )
            )
        else:
            boxes.append(
                (
                    _get_width_of_boxes(awardsLength),
                    _get_height_of_boxes(1),
                )
            )

    image = newImage(
        (
            math.ceil(max([b[0] for b in boxes]))
            + STORAGE_MARGIN_LEFT
            + STORAGE_MARGIN_RIGHT,
            math.ceil(sum([b[1] for b in boxes]))
            + STORAGE_MARGIN_TOP
            + STORAGE_MARGIN_BOTTOM,
        ),
        STORAGE_BACKGROUND_COLOR,
    )

    draw = PIL.ImageDraw.Draw(image)

    drawTop: float = STORAGE_MARGIN_TOP
    drawLeft: float = STORAGE_MARGIN_LEFT

    pointer = 0

    for level in getAllLevelsOfAwardList(getAllAwardsOfOneUser(uid)):
        tbox = textBox(f"稀有度为【{level.name}】的全部小哥", STORAGE_TEXT_FONT)

        color = STORAGE_TEXT_COLOR

        if level.name in STORAGE_SPECIFIED_COLOR.keys():
            color = STORAGE_SPECIFIED_COLOR[level.name]

        drawText(
            draw,
            f"稀有度为【{level.name}】的全部小哥",
            drawLeft - tbox.left,
            drawTop,
            color,
            STORAGE_TEXT_FONT,
        )

        drawTop += STORAGE_BOX_MARGIN_TOP + boxes[pointer][1]
        drawLeft += STORAGE_BOX_MARGIN_LEFT

        levelAwards = [a for a in awards if a.levelId == level.lid]

        for ind, award in enumerate(levelAwards):
            colX = ind % STORAGE_BOX_XCOUNT_MAX
            colY = ind // STORAGE_BOX_XCOUNT_MAX

            xDelta = colX * (STORAGE_BOX_WIDTH + STORAGE_BOX_PADDING_X)
            yDelta = (
                colY * (STORAGE_BOX_HEIGHT + STORAGE_BOX_PADDING_Y)
                + boxes[pointer][1]
            )

            drawStorageBlock(
                image,
                award,
                getAwardCoundOfOneUser(uid, award.aid),
                drawLeft + xDelta,
                drawTop + yDelta,
                STORAGE_BOX_SCALE,
            )

        drawLeft -= STORAGE_BOX_MARGIN_LEFT
        drawTop += (
            _get_height_of_boxes(math.ceil(len(levelAwards) / STORAGE_BOX_XCOUNT_MAX))
            - STORAGE_BOX_MARGIN_TOP
        )

        pointer += 2

    print(boxes)

    return image, time.time() - beginTime
