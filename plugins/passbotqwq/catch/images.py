from functools import cache
import math
import os
import time

from sqlalchemy import select

import PIL
import PIL.ImageDraw

from nonebot.log import logger
from nonebot_plugin_orm import async_scoped_session, get_session
from nonebot import get_driver

from .models.crud import selectAllLevelUserObtained

from .models.Basics import Award, AwardCountStorage, Level, UserData

from .cores import Pick
from ..putils.draw.images import (
    addUponPaste,
    fastPaste,
    fromOpenCVImage,
    loadImage,
    toOpenCVImage,
    resize,
)
from ..putils.draw.texts import drawText, textBox, textFont, Fonts
from ..putils.draw.typing import PILImage, PillowColorLike, PillowColorLikeStrong
from ..putils.draw import newImage

from .data import (
    DBAward,
    getLevelOfAward,
    userHaveAward,
)


GLOBAL_BACKGROUND_COLOR = "#696361"

IMAGE_RAW_WIDTH = 2000
IMAGE_RAW_HEIGHT = 1600

STORAGE_MARGIN_LEFT = 30
STORAGE_MARGIN_RIGHT = 30
STORAGE_MARGIN_TOP = 30
STORAGE_MARGIN_BOTTOM = 30

STORAGE_AWARD_BOX_XCOUNT_MAX = 4

STORAGE_TITLE_TEXT_COLOR = "#FFFFFF"
STORAGE_TITLE_TEXT_FONT = textFont(Fonts.JINGNAN_BOBO_HEI, 48)

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
    1: "#d1cccb",
    2: "#cdebc3",
    3: "#c5dceb",
    4: "#ecdff5",
    5: "#fae9bb",
}

CAUGHT_BOX_MARGIN_LEFT = 0
CAUGHT_BOX_MARGIN_RIGHT = 0
CAUGHT_BOX_MARGIN_TOP = 0
CAUGHT_BOX_MARGIN_BOTTOM = 0


__cached_box_image: dict[tuple[str, PillowColorLike, float], PILImage] = {}


async def drawAwardBoxImage(
    awardURL: str,
    background: PillowColorLike = AWARD_BOX_BACKGROUND_COLOR,
    scale: float = AWARD_BOX_SCALE,
):
    _key = (awardURL, background, scale)

    if _key in __cached_box_image:
        return __cached_box_image[_key]

    base = await newImage(
        (int(IMAGE_RAW_WIDTH * scale), int(IMAGE_RAW_HEIGHT * scale)),
        background,
    )

    await addUponPaste(
        base,
        await resize(
            await loadImage(awardURL),
            int(IMAGE_RAW_WIDTH * scale),
            int(IMAGE_RAW_HEIGHT * scale),
        ),
        0,
        0,
    )

    __cached_box_image[_key] = base
    return base


async def drawAwardBox(
    award: Award,
    count: str = "",
    bgColor: str = AWARD_BOX_BACKGROUND_COLOR,
    scale: float = AWARD_BOX_SCALE,
):
    base = await newImage(
        (
            int(IMAGE_RAW_WIDTH * scale),
            int(IMAGE_RAW_HEIGHT * scale + AWARD_BOX_NAME_LINE_HEIGHT),
        ),
        GLOBAL_BACKGROUND_COLOR,
    )

    await addUponPaste(base, await drawAwardBoxImage(award.img_path, bgColor), 0, 0)

    draw = PIL.ImageDraw.Draw(base)
    tbox = textBox(count, AWARD_BOX_COUNT_FONT)

    await drawText(
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

    color = bgColor

    await drawText(
        draw,
        award.name,
        AWARD_BOX_NAME_LEFT + IMAGE_RAW_WIDTH * scale / 2 - tbox.right / 2,
        IMAGE_RAW_HEIGHT * scale + AWARD_BOX_NAME_TOP,
        color,
        AWARD_BOX_NAME_FONT,
    )

    return base


async def drawStorage(
    session: async_scoped_session,
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
    awardBoxes: list[list[AwardCountStorage]] = []

    level_select = selectAllLevelUserObtained(uid).order_by(Level.weight)
    levels = (await session.execute(level_select)).scalars()

    for level in levels:
        award_counter_select = (
            select(AwardCountStorage)
            .filter(AwardCountStorage.target_user.has(UserData.qq_id == uid))
            .filter(AwardCountStorage.target_award.has(Award.level == level))
            .order_by(-AwardCountStorage.award_count)
        )

        award_counters = (await session.execute(award_counter_select)).all()

        lines.append(math.ceil(len(award_counters) / maxRowCount))
        awardBoxes.append([ac.tuple()[0] for ac in award_counters])

    image = await newImage(
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

    for awardStorages in awardBoxes:
        targetLevel = awardStorages[0].target_award.level

        bgc = AWARD_BOX_BACKGROUND_COLOR

        if targetLevel.data_id in AWARD_BOX_BACKGROUND_COLOR_SPECIFIED.keys():
            bgc = AWARD_BOX_BACKGROUND_COLOR_SPECIFIED[targetLevel.data_id]  # type: ignore

        for i, awardStorage in enumerate(awardStorages):
            award = awardStorage.target_award

            box = await drawAwardBox(award, str(awardStorage.award_count), bgc, scale)

            await addUponPaste(
                image,
                box,
                int(
                    drawLeft + (i % maxRowCount) * (IMAGE_RAW_WIDTH * scale + paddingX)
                ),
                int(drawTop + (i // maxRowCount) * (boxHeight + paddingY)),
            )

        drawTop += math.ceil(len(awardStorages) / maxRowCount) * (boxHeight + paddingY)

    return image, time.time() - beginTime


@cache
def drawAwardBoxImageHidden():
    return drawAwardBoxImage(os.path.join(".", "res", "catch", "blank_placeholder.png"))


async def drawStatus(
    uid: int,
    scale: float = AWARD_BOX_SCALE,
):
    begin = time.time()

    awardsToDraw = DBAward().sorted(lambda a: (getLevelOfAward(a).weight, a.aid))

    lines = math.ceil(len(awardsToDraw) / STATUS_MAX_ROW_COUNT)

    image = await newImage(
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

    _image = await toOpenCVImage(image)

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

        subImage = await (
            drawAwardBoxImage(award.imgPath, bg)
            if userHaveAward(uid, award)
            else drawAwardBoxImageHidden()
        )
        await fastPaste(_image, await toOpenCVImage(subImage), x, y)

    return await fromOpenCVImage(_image), time.time() - begin


async def drawCaughtBox(pick: Pick):
    sub = await drawAwardBox(pick.award, f"{pick.fromNumber}→{pick.toNumber}")

    image = await newImage(
        (
            sub.size[0] + CAUGHT_BOX_MARGIN_LEFT + CAUGHT_BOX_MARGIN_RIGHT,
            sub.size[1] + CAUGHT_BOX_MARGIN_TOP + CAUGHT_BOX_MARGIN_BOTTOM,
        ),
        GLOBAL_BACKGROUND_COLOR,
    )

    image.paste(sub, (CAUGHT_BOX_MARGIN_LEFT, CAUGHT_BOX_MARGIN_TOP))

    return image


driver = get_driver()


@driver.on_startup
async def preDrawEverything():
    session = get_session()
    awards = (await session.execute(select(Award))).scalars()

    for award in awards:
        bg = AWARD_BOX_BACKGROUND_COLOR

        if award.level_id in AWARD_BOX_BACKGROUND_COLOR_SPECIFIED.keys():
            bg = AWARD_BOX_BACKGROUND_COLOR_SPECIFIED[award.level_id]  # type: ignore

        await drawAwardBoxImage(award.img_path, bg)

    logger.info("Predraw finished")
