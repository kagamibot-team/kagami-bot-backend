from functools import cache
import math
import os
import time

import PIL
import PIL.ImageDraw

from .cores import Pick
from .models import Award
from ..putils.threading import make_async
from ..putils.draw.images import (
    addUponPaste,
    fastPaste,
    fromOpenCVImage,
    loadImage,
    toOpenCVImage,
)
from ..putils.draw.texts import drawText, textBox, textFont, Fonts
from ..putils.draw.typing import IMAGE, PILLOW_COLOR_LIKE
from ..putils.draw import newImage

from .data import (
    DBAward,
    DBLevel,
    getAllAwards,
    getAllAwardsOfOneUser,
    getAllLevelsOfAwardList,
    getAwardByAwardId,
    getAwardCountOfOneUser,
    getLevelOfAward,
    getUserAwardCounter,
    userHaveAward,
)


GLOBAL_BACKGROUND_COLOR = "#696361"

IMAGE_RAW_WIDTH = 2000
IMAGE_RAW_HEIGHT = 1600

STORAGE_MARGIN_LEFT = 60
STORAGE_MARGIN_RIGHT = 60
STORAGE_MARGIN_TOP = 140
STORAGE_MARGIN_BOTTOM = 40

STORAGE_AWARD_BOX_XCOUNT_MAX = 4

STORAGE_TITLE_TEXT_COLOR = "#FFFFFF"
STORAGE_TITLE_TEXT_FONT = textFont(Fonts.JINGNAN_BOBO_HEI, 48)
STORAGE_TITLE_SPECIFIED_COLOR = {
    0: "#d1cccb",
    1: "#92d47b",
    6: "#89c2e8",
    2: "#d8adf7",
    7: "#facb4b",
}

AWARD_BOX_PADDING_X = 10
AWARD_BOX_PADDING_Y = 10
AWARD_BOX_MARGIN_LEFT = 0
AWARD_BOX_MARGIN_RIGHT = 0
AWARD_BOX_MARGIN_TOP = -20
AWARD_BOX_MARGIN_BOTTOM = 120

AWARD_BOX_SCALE = 0.08

AWARD_BOX_BACKGROUND_COLOR = "#9e9d95"

AWARD_BOX_COUNT_FONT = textFont(Fonts.FONT_HARMONYOS_SANS_BLACK, 36)
AWARD_BOX_COUNT_COLOR = STORAGE_TITLE_TEXT_COLOR
AWARD_BOX_COUNT_STROKE_COLOR = "#000000"
AWARD_BOX_COUNT_STROKE_WIDTH = 2

AWARD_BOX_COUNT_DX = 4
AWARD_BOX_COUNT_DY = -4

AWARD_BOX_NAME_TOP = 8
AWARD_BOX_NAME_LEFT = 4
AWARD_BOX_NAME_LINE_HEIGHT = 40
AWARD_BOX_NAME_FONT = textFont(Fonts.JIANGCHENG_YUANTI, 22)
AWARD_BOX_NAME_COLOR = STORAGE_TITLE_TEXT_COLOR
AWARD_BOX_NAME_STROKE_COLOR = "#000000"
AWARD_BOX_NAME_STROKE_WIDTH = 0
AWARD_BOX_NAME_COLOR_SPECIFIED = {
    0: "#d1cccb",
    1: "#92d47b",
    6: "#89c2e8",
    2: "#d8adf7",
    7: "#facb4b",
}
AWARD_BOX_NAME_STROKE_COLOR_SPECIFIED: dict[int, str] = {}
AWARD_BOX_NAME_STROKE_WIDTH_SPECIFIED: dict[int, int] = {}

STATUS_MARGIN_LEFT = 60
STATUS_MARGIN_RIGHT = 60
STATUS_MARGIN_TOP = 140
STATUS_MARGIN_BOTTOM = 40

STATUS_MAX_ROW_COUNT = 6

STATUS_PADDING_X = 10
STATUS_PADDING_Y = 10

AWARD_BOX_BACKGROUND_COLOR_SPECIFIED = {
    0: "#d1cccb",
    1: "#cdebc3",
    6: "#c5dceb",
    2: "#ecdff5",
    7: "#fae9bb",
}

CAUGHT_BOX_MARGIN_LEFT = 0
CAUGHT_BOX_MARGIN_RIGHT = 0
CAUGHT_BOX_MARGIN_TOP = 0
CAUGHT_BOX_MARGIN_BOTTOM = 0

# 计算值
AWARD_BOX_IMAGE_WIDTH = IMAGE_RAW_WIDTH * AWARD_BOX_SCALE
AWARD_BOX_IMAGE_HEIGHT = IMAGE_RAW_HEIGHT * AWARD_BOX_SCALE
AWARD_BOX_WIDTH = AWARD_BOX_IMAGE_WIDTH
AWARD_BOX_HEIGHT = AWARD_BOX_IMAGE_HEIGHT + AWARD_BOX_NAME_LINE_HEIGHT


def _get_width_of_boxes(count: int):
    return (
        AWARD_BOX_MARGIN_LEFT
        + AWARD_BOX_MARGIN_RIGHT
        + AWARD_BOX_PADDING_X * (count - 1)
        + AWARD_BOX_WIDTH * count
    )


def _get_height_of_boxes(lines: int):
    return (
        AWARD_BOX_MARGIN_TOP
        + AWARD_BOX_MARGIN_BOTTOM
        + AWARD_BOX_PADDING_Y * (lines - 1)
        + AWARD_BOX_HEIGHT * lines
    )


__cached_box_image: dict[tuple[str, PILLOW_COLOR_LIKE], IMAGE] = {}


def drawAwardBoxImage(
    awardURL: str, background: PILLOW_COLOR_LIKE = AWARD_BOX_BACKGROUND_COLOR
):
    _key = (awardURL, background)

    if _key in __cached_box_image:
        return __cached_box_image[_key]

    base = newImage(
        (int(AWARD_BOX_IMAGE_WIDTH), int(AWARD_BOX_IMAGE_HEIGHT)),
        background,
    )
    addUponPaste(
        base,
        loadImage(awardURL).resize(
            (
                int(AWARD_BOX_IMAGE_WIDTH),
                int(AWARD_BOX_IMAGE_HEIGHT),
            )
        ),
        0,
        0,
    )

    __cached_box_image[_key] = base
    return base


def drawAwardBox(
    award: Award,
    count: str = "",
    bgColor: PILLOW_COLOR_LIKE = AWARD_BOX_BACKGROUND_COLOR,
):
    base = newImage(
        (int(AWARD_BOX_WIDTH), int(AWARD_BOX_HEIGHT)), GLOBAL_BACKGROUND_COLOR
    )

    base.paste(drawAwardBoxImage(award.imgPath, bgColor), (0, 0))

    draw = PIL.ImageDraw.Draw(base)
    tbox = textBox(count, AWARD_BOX_COUNT_FONT)

    drawText(
        draw,
        count,
        AWARD_BOX_COUNT_DX,
        AWARD_BOX_IMAGE_HEIGHT - tbox.bottom + AWARD_BOX_COUNT_DY,
        AWARD_BOX_COUNT_COLOR,
        AWARD_BOX_COUNT_FONT,
        AWARD_BOX_COUNT_STROKE_COLOR,
        AWARD_BOX_COUNT_STROKE_WIDTH,
    )

    tbox = textBox(award.name, AWARD_BOX_NAME_FONT)

    color = AWARD_BOX_NAME_COLOR

    if award.levelId in AWARD_BOX_NAME_COLOR_SPECIFIED.keys():
        color = AWARD_BOX_NAME_COLOR_SPECIFIED[award.levelId]

    s_color = AWARD_BOX_NAME_STROKE_COLOR

    if award.levelId in AWARD_BOX_NAME_STROKE_COLOR_SPECIFIED.keys():
        s_color = AWARD_BOX_NAME_STROKE_COLOR_SPECIFIED[award.levelId]

    s_width = AWARD_BOX_NAME_STROKE_WIDTH

    if award.levelId in AWARD_BOX_NAME_STROKE_WIDTH_SPECIFIED.keys():
        s_width = AWARD_BOX_NAME_STROKE_WIDTH_SPECIFIED[award.levelId]

    drawText(
        draw,
        award.name,
        AWARD_BOX_NAME_LEFT + AWARD_BOX_WIDTH / 2 - tbox.right / 2,
        AWARD_BOX_IMAGE_HEIGHT + AWARD_BOX_NAME_TOP,
        color,
        AWARD_BOX_NAME_FONT,
        s_color,
        s_width,
    )

    return base


@make_async
def drawStorage(uid: int):
    beginTime = time.time()
    lines = 0

    awardBoxes: list[list[Award]] = []

    for level in DBLevel().userHave(uid).sorted(lambda l: -l.weight):
        awards = (
            DBAward()
            .lid(level.lid)
            .userHave(uid)
            .sorted(lambda a: -getUserAwardCounter(uid)[a.aid])
        )

        lines += math.ceil(len(awards) / STORAGE_AWARD_BOX_XCOUNT_MAX)
        awardBoxes.append(awards)

    image = newImage(
        (
            int(
                STORAGE_MARGIN_LEFT
                + STORAGE_MARGIN_RIGHT
                + AWARD_BOX_WIDTH * STORAGE_AWARD_BOX_XCOUNT_MAX
                + AWARD_BOX_PADDING_X * (STORAGE_AWARD_BOX_XCOUNT_MAX - 1)
            ),
            int(
                STORAGE_MARGIN_TOP
                + STORAGE_MARGIN_BOTTOM
                + AWARD_BOX_HEIGHT * lines
                + AWARD_BOX_PADDING_Y * (lines - 1)
            ),
        ),
        GLOBAL_BACKGROUND_COLOR,
    )

    drawTop = STORAGE_MARGIN_TOP
    drawLeft = STORAGE_MARGIN_LEFT

    for awards in awardBoxes:
        bgc = AWARD_BOX_BACKGROUND_COLOR

        if awards[0].levelId in AWARD_BOX_BACKGROUND_COLOR_SPECIFIED.keys():
            bgc = AWARD_BOX_BACKGROUND_COLOR_SPECIFIED[awards[0].levelId]

        for i, award in enumerate(awards):
            box = drawAwardBox(award, str(getAwardCountOfOneUser(uid, award.aid)), bgc)

            addUponPaste(
                image,
                box,
                int(
                    drawLeft
                    + (i % STORAGE_AWARD_BOX_XCOUNT_MAX)
                    * (AWARD_BOX_WIDTH + AWARD_BOX_PADDING_X)
                ),
                int(
                    drawTop
                    + (i // STORAGE_AWARD_BOX_XCOUNT_MAX)
                    * (AWARD_BOX_HEIGHT + AWARD_BOX_PADDING_Y)
                ),
            )

        drawTop += math.ceil(len(awards) / STORAGE_AWARD_BOX_XCOUNT_MAX) * (
            AWARD_BOX_HEIGHT + AWARD_BOX_PADDING_Y
        )

    return image, time.time() - beginTime
    beginTime = time.time()
    boxes: list[tuple[float, float]] = []

    awards = getAllAwardsOfOneUser(uid)

    for level in getAllLevelsOfAwardList(getAllAwardsOfOneUser(uid)):
        tbox = textBox(f"{level.name}", STORAGE_TITLE_TEXT_FONT)
        boxes.append((tbox.right - tbox.left, tbox.bottom - tbox.top))

        awardsLength = len([a for a in awards if a.levelId == level.lid])

        if awardsLength >= STORAGE_AWARD_BOX_XCOUNT_MAX:
            boxes.append(
                (
                    _get_width_of_boxes(STORAGE_AWARD_BOX_XCOUNT_MAX),
                    _get_height_of_boxes(
                        math.ceil(awardsLength / STORAGE_AWARD_BOX_XCOUNT_MAX)
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
        GLOBAL_BACKGROUND_COLOR,
    )

    draw = PIL.ImageDraw.Draw(image)

    drawTop: float = STORAGE_MARGIN_TOP
    drawLeft: float = STORAGE_MARGIN_LEFT

    pointer = 0

    for level in getAllLevelsOfAwardList(getAllAwardsOfOneUser(uid)):
        tbox = textBox(f"{level.name}", STORAGE_TITLE_TEXT_FONT)

        color = STORAGE_TITLE_TEXT_COLOR

        if level.lid in STORAGE_TITLE_SPECIFIED_COLOR.keys():
            color = STORAGE_TITLE_SPECIFIED_COLOR[level.lid]

        drawText(
            draw,
            f"{level.name}",
            drawLeft - tbox.left,
            drawTop,
            color,
            STORAGE_TITLE_TEXT_FONT,
        )

        drawTop += AWARD_BOX_MARGIN_TOP + boxes[pointer][1]
        drawLeft += AWARD_BOX_MARGIN_LEFT

        levelAwards = [a for a in awards if a.levelId == level.lid]

        for ind, award in enumerate(levelAwards):
            colX = ind % STORAGE_AWARD_BOX_XCOUNT_MAX
            colY = ind // STORAGE_AWARD_BOX_XCOUNT_MAX

            xDelta = colX * (AWARD_BOX_WIDTH + AWARD_BOX_PADDING_X)
            yDelta = colY * (AWARD_BOX_HEIGHT + AWARD_BOX_PADDING_Y) + boxes[pointer][1]

            addUponPaste(
                image,
                drawAwardBox(award, str(getAwardCountOfOneUser(uid, award.aid))),
                int(drawLeft + xDelta),
                int(drawTop + yDelta),
            )

        drawLeft -= AWARD_BOX_MARGIN_LEFT
        drawTop += (
            _get_height_of_boxes(
                math.ceil(len(levelAwards) / STORAGE_AWARD_BOX_XCOUNT_MAX)
            )
            - AWARD_BOX_MARGIN_TOP
        )

        pointer += 2

    print(boxes)

    return image, time.time() - beginTime


@cache
def drawAwardBoxImageHidden():
    return drawAwardBoxImage(os.path.join(".", "res", "catch", "blank_placeholder.png"))


@make_async
def drawStatus(uid: int):
    begin = time.time()

    awardsToDraw = sorted(
        getAllAwards(), key=lambda a: (getLevelOfAward(a).weight, a.aid)
    )

    lines = math.ceil(len(awardsToDraw) / STATUS_MAX_ROW_COUNT)

    image = newImage(
        (
            int(
                STATUS_MARGIN_LEFT
                + STATUS_MARGIN_RIGHT
                + AWARD_BOX_IMAGE_WIDTH * STATUS_MAX_ROW_COUNT
                + AWARD_BOX_PADDING_X * (STATUS_MAX_ROW_COUNT - 1)
            ),
            int(
                STATUS_MARGIN_TOP
                + STATUS_MARGIN_BOTTOM
                + AWARD_BOX_IMAGE_HEIGHT * lines
                + STATUS_PADDING_Y * (lines - 1)
            ),
        ),
        GLOBAL_BACKGROUND_COLOR,
    )

    _image = toOpenCVImage(image)

    for i, award in enumerate(awardsToDraw):
        px = i % STATUS_MAX_ROW_COUNT
        py = i // STATUS_MAX_ROW_COUNT

        x = int(STATUS_MARGIN_LEFT + px * (AWARD_BOX_IMAGE_WIDTH + AWARD_BOX_PADDING_X))
        y = int(
            STATUS_MARGIN_RIGHT + py * (AWARD_BOX_IMAGE_HEIGHT + AWARD_BOX_PADDING_Y)
        )

        bg = AWARD_BOX_BACKGROUND_COLOR

        level = getLevelOfAward(award)

        if level.lid in AWARD_BOX_BACKGROUND_COLOR_SPECIFIED.keys():
            bg = AWARD_BOX_BACKGROUND_COLOR_SPECIFIED[level.lid]

        subImage = (
            drawAwardBoxImage(award.imgPath, bg)
            if userHaveAward(uid, award)
            else drawAwardBoxImageHidden()
        )
        # image.paste(subImage, (x, y))
        fastPaste(_image, toOpenCVImage(subImage), x, y)

    return fromOpenCVImage(_image), time.time() - begin


@make_async
def drawCaughtBox(pick: Pick):
    sub = drawAwardBox(
        getAwardByAwardId(pick.awardId), f"{pick.fromNumber}→{pick.toNumber}"
    )

    image = newImage(
        (
            sub.size[0] + CAUGHT_BOX_MARGIN_LEFT + CAUGHT_BOX_MARGIN_RIGHT,
            sub.size[1] + CAUGHT_BOX_MARGIN_TOP + CAUGHT_BOX_MARGIN_BOTTOM,
        ),
        GLOBAL_BACKGROUND_COLOR,
    )

    image.paste(sub, (CAUGHT_BOX_MARGIN_LEFT, CAUGHT_BOX_MARGIN_TOP))

    return image
