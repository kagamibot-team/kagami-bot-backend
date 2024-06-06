from functools import cache
import math
import os
from threading import Thread
import time

import PIL
import PIL.ImageDraw

from nonebot.log import logger

from .cores import Pick
from .pydantic_models import PydanticAward
from ..putils.threading import make_async
from ..putils.draw.images import (
    addUponPaste,
    fastPaste,
    fromOpenCVImage,
    loadImage,
    toOpenCVImage,
)
from ..putils.draw.texts import drawText, textBox, textFont, Fonts
from ..putils.draw.typing import PILImage, PillowColorLike
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

STORAGE_MARGIN_LEFT = 0
STORAGE_MARGIN_RIGHT = 0
STORAGE_MARGIN_TOP = 0
STORAGE_MARGIN_BOTTOM = 0

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

AWARD_BOX_SCALE = 0.06

AWARD_BOX_BACKGROUND_COLOR = "#9e9d95"

AWARD_BOX_COUNT_FONT = textFont(Fonts.FONT_HARMONYOS_SANS_BLACK, 27)
AWARD_BOX_COUNT_COLOR = STORAGE_TITLE_TEXT_COLOR
AWARD_BOX_COUNT_STROKE_COLOR = "#000000"
AWARD_BOX_COUNT_STROKE_WIDTH = 2

AWARD_BOX_COUNT_DX = 4
AWARD_BOX_COUNT_DY = -4

AWARD_BOX_NAME_TOP = 8
AWARD_BOX_NAME_LEFT = 4
AWARD_BOX_NAME_LINE_HEIGHT = 40
AWARD_BOX_NAME_FONT = textFont(Fonts.FONT_HARMONYOS_SANS, 16)
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

STATUS_MARGIN_LEFT = 0
STATUS_MARGIN_RIGHT = 0
STATUS_MARGIN_TOP = 0
STATUS_MARGIN_BOTTOM = 0

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


__cached_box_image: dict[tuple[str, PillowColorLike, float], PILImage] = {}


def drawAwardBoxImage(
    awardURL: str,
    background: PillowColorLike = AWARD_BOX_BACKGROUND_COLOR,
    scale: float = AWARD_BOX_SCALE,
):
    _key = (awardURL, background, scale)

    if _key in __cached_box_image:
        return __cached_box_image[_key]

    base = newImage(
        (int(IMAGE_RAW_WIDTH * scale), int(IMAGE_RAW_HEIGHT * scale)),
        background,
    )

    addUponPaste(
        base,
        loadImage(awardURL).resize(
            (
                int(IMAGE_RAW_WIDTH * scale),
                int(IMAGE_RAW_HEIGHT * scale),
            )
        ),
        0,
        0,
    )

    __cached_box_image[_key] = base
    return base


def drawAwardBox(
    award: PydanticAward,
    count: str = "",
    bgColor: PillowColorLike = AWARD_BOX_BACKGROUND_COLOR,
    scale: float = AWARD_BOX_SCALE,
):
    base = newImage(
        (
            int(IMAGE_RAW_WIDTH * scale),
            int(IMAGE_RAW_HEIGHT * scale + AWARD_BOX_NAME_LINE_HEIGHT),
        ),
        GLOBAL_BACKGROUND_COLOR,
    )

    base.paste(drawAwardBoxImage(award.imgPath, bgColor), (0, 0))

    draw = PIL.ImageDraw.Draw(base)
    tbox = textBox(count, AWARD_BOX_COUNT_FONT)

    drawText(
        draw,
        count,
        AWARD_BOX_COUNT_DX,
        IMAGE_RAW_HEIGHT * scale - tbox.bottom + AWARD_BOX_COUNT_DY,
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
        AWARD_BOX_NAME_LEFT + IMAGE_RAW_WIDTH * scale / 2 - tbox.right / 2,
        IMAGE_RAW_HEIGHT * scale + AWARD_BOX_NAME_TOP,
        color,
        AWARD_BOX_NAME_FONT,
        s_color,
        s_width,
    )

    return base


@make_async
def drawStorage(
    uid: int,
    scale: float = AWARD_BOX_SCALE,
    maxRowCount: int = STORAGE_AWARD_BOX_XCOUNT_MAX,
    marginLeft: int = STORAGE_MARGIN_LEFT,
    marginRight: int = STORAGE_MARGIN_RIGHT,
    marginTop: int = STORAGE_MARGIN_TOP,
    marginBottom: int = STORAGE_MARGIN_BOTTOM,
    paddingX: int = AWARD_BOX_PADDING_X,
    paddingY: int = AWARD_BOX_PADDING_Y,
    backgroundColor: PillowColorLike = GLOBAL_BACKGROUND_COLOR,
):
    beginTime = time.time()
    lines: list[int] = []

    boxHeight = IMAGE_RAW_HEIGHT * scale + AWARD_BOX_NAME_LINE_HEIGHT
    awardBoxes: list[list[PydanticAward]] = []

    print("drawStatus0", time.time() - beginTime)

    for level in DBLevel().userHave(uid).sorted(lambda l: l.weight):
        awards = (
            DBAward()
            .lid(level.lid)
            .userHave(uid)
            .sorted(lambda a: -getAwardCountOfOneUser(uid, a.aid))
        )

        lines.append(math.ceil(len(awards) / maxRowCount))
        awardBoxes.append(awards)

    print("drawStatus1", time.time() - beginTime)

    image = newImage(
        (
            int(
                marginLeft
                + marginRight
                + IMAGE_RAW_WIDTH * scale * maxRowCount
                + paddingX * (maxRowCount - 1)
            ),
            int(
                marginTop
                + marginBottom
                + boxHeight * sum(lines)
                + paddingY * (sum(lines) - 1)
            ),
        ),
        backgroundColor,
    )

    drawTop = marginTop
    drawLeft = marginLeft

    for awards in awardBoxes:
        bgc = AWARD_BOX_BACKGROUND_COLOR

        if awards[0].levelId in AWARD_BOX_BACKGROUND_COLOR_SPECIFIED.keys():
            bgc = AWARD_BOX_BACKGROUND_COLOR_SPECIFIED[awards[0].levelId]

        for i, award in enumerate(awards):
            box = drawAwardBox(
                award, str(getAwardCountOfOneUser(uid, award.aid)), bgc, scale
            )

            addUponPaste(
                image,
                box,
                int(
                    drawLeft + (i % maxRowCount) * (IMAGE_RAW_WIDTH * scale + paddingX)
                ),
                int(drawTop + (i // maxRowCount) * (boxHeight + paddingY)),
            )

        drawTop += math.ceil(len(awards) / maxRowCount) * (boxHeight + paddingY)

    print("drawStatus2", time.time() - beginTime)

    return image, time.time() - beginTime


@cache
def drawAwardBoxImageHidden():
    return drawAwardBoxImage(os.path.join(".", "res", "catch", "blank_placeholder.png"))


@make_async
def drawStatus(
    uid: int,
    scale: float = AWARD_BOX_SCALE,
):
    begin = time.time()

    awardsToDraw = DBAward().sorted(lambda a: (getLevelOfAward(a).weight, a.aid))

    lines = math.ceil(len(awardsToDraw) / STATUS_MAX_ROW_COUNT)

    image = newImage(
        (
            int(
                STATUS_MARGIN_LEFT
                + STATUS_MARGIN_RIGHT
                + IMAGE_RAW_WIDTH * scale * STATUS_MAX_ROW_COUNT
                + AWARD_BOX_PADDING_X * (STATUS_MAX_ROW_COUNT - 1)
            ),
            int(
                STATUS_MARGIN_TOP
                + STATUS_MARGIN_BOTTOM
                + IMAGE_RAW_HEIGHT * scale * lines
                + STATUS_PADDING_Y * (lines - 1)
            ),
        ),
        GLOBAL_BACKGROUND_COLOR,
    )

    _image = toOpenCVImage(image)

    for i, award in enumerate(awardsToDraw):
        px = i % STATUS_MAX_ROW_COUNT
        py = i // STATUS_MAX_ROW_COUNT

        x = int(
            STATUS_MARGIN_LEFT + px * (IMAGE_RAW_WIDTH * scale + AWARD_BOX_PADDING_X)
        )
        y = int(
            STATUS_MARGIN_TOP + py * (IMAGE_RAW_HEIGHT * scale + AWARD_BOX_PADDING_Y)
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
        fastPaste(_image, toOpenCVImage(subImage), x, y)

    return fromOpenCVImage(_image), time.time() - begin


@make_async
def drawCaughtBox(pick: Pick):
    sub = drawAwardBox(pick.award(), f"{pick.fromNumber}→{pick.toNumber}")

    image = newImage(
        (
            sub.size[0] + CAUGHT_BOX_MARGIN_LEFT + CAUGHT_BOX_MARGIN_RIGHT,
            sub.size[1] + CAUGHT_BOX_MARGIN_TOP + CAUGHT_BOX_MARGIN_BOTTOM,
        ),
        GLOBAL_BACKGROUND_COLOR,
    )

    image.paste(sub, (CAUGHT_BOX_MARGIN_LEFT, CAUGHT_BOX_MARGIN_TOP))

    return image


class PredrawEverything(Thread):
    def run(self) -> None:
        awards = DBAward()()

        for award in awards:
            bg = AWARD_BOX_BACKGROUND_COLOR

            if award.levelId in AWARD_BOX_BACKGROUND_COLOR_SPECIFIED.keys():
                bg = AWARD_BOX_BACKGROUND_COLOR_SPECIFIED[award.levelId]

            drawAwardBoxImage(award.imgPath, bg)

        logger.info("Predraw finished.")


PredrawEverything().start()
