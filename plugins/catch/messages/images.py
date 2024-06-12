import base64
import cProfile
import os
import time
from typing_extensions import deprecated
import PIL
import PIL.ImageDraw

import PIL.ImageFont
import nonebot
from sqlalchemy import select
from nonebot.log import logger
from nonebot_plugin_orm import async_scoped_session, get_session
from nonebot import get_driver

from ..models import *

from ..putils.draw.images import (
    addUponPaste,
    horizontalPile,
    verticalPile,
    combineABunchOfImage,
)
from ..putils.draw.texts import (
    VerticalAnchor,
    drawABoxOfText,
    drawLimitedBoxOfText,
    drawText,
    textFont,
    Fonts,
)
from ..putils.draw.typing import PILImage
from ..putils.draw.images import newImage
from ..putils.config import config

from ..images import display_box, catch, refBookBox


GLOBAL_SCALAR = 1.5


@deprecated("Use images.components.display_box instead")
async def drawAwardBoxImage(
    awardURL: str, background: str = "#9e9d95", new: bool = False
):
    base = await newImage(
        (int(120 * GLOBAL_SCALAR), int(96 * GLOBAL_SCALAR)), "#696361"
    )

    await addUponPaste(
        base,
        await display_box(background, awardURL, new),
        0,
        0,
    )

    return base


@deprecated("Use images.components.display_box instead")
async def drawAwardBox(
    awardURL: str,
    awardName: str | None,
    count: str,
    background: str = "#9e9d95",
    new: bool = False,
):
    if awardName:
        base = await verticalPile(
            [
                await drawAwardBoxImage(awardURL, background, new),
                await drawLimitedBoxOfText(
                    awardName,
                    int(120 * GLOBAL_SCALAR),
                    "center",
                    "center",
                    int(18 * GLOBAL_SCALAR),
                    background,
                    Fonts.HARMONYOS_SANS,
                    int(14 * GLOBAL_SCALAR),
                ),
            ],
            int(3 * GLOBAL_SCALAR),
            "center",
            "#696361",
        )
    else:
        base = await drawAwardBoxImage(awardURL, background, new)

    draw = PIL.ImageDraw.Draw(base)

    await drawText(
        draw,
        count,
        int(4 * GLOBAL_SCALAR),
        int(92 * GLOBAL_SCALAR),
        "#FFFFFF",
        textFont(Fonts.HARMONYOS_SANS_BLACK, int(27 * GLOBAL_SCALAR)),
        strokeColor="#000000",
        strokeWidth=int(2 * GLOBAL_SCALAR),
        verticalAlign=VerticalAnchor.bottom,
    )

    return base


async def drawStorage(session: async_scoped_session, user: User):
    awards: list[PILImage] = []

    acs = await getUserStorages(session, user)

    for ac in acs:
        award = ac.award
        count = ac.count

        awards.append(
            await refBookBox(
                award.name,
                str(count),
                award.level.color_code,
                await getAwardImage(session, user, award),
            )
        )

    return await combineABunchOfImage(
        0, 0, awards, 6, "#9B9690", "top", "left", 30, 30, 60, 30
    )


async def drawStatus(session: async_scoped_session, user: User | None):
    boxes: list[PILImage] = []
    levels = await getAllLevels(session)

    for level in levels:
        allAwards = await getAllAwardsInLevel(session, level)

        if user:
            userCollected = await getUserStoragesByLevel(session, user, level)
            title = f"{level.name}：{len(userCollected)} / {len(allAwards)}"
        else:
            userCollected = []
            title = level.name

        boxes.append(
            await drawABoxOfText(
                title,
                level.color_code,
                textFont(Fonts.JINGNAN_BOBO_HEI, int(48 * GLOBAL_SCALAR)),
                background="#696361",
                marginTop=int(30 * GLOBAL_SCALAR),
                marginLeft=0,
                marginRight=0,
                marginBottom=int(20 * GLOBAL_SCALAR),
            )
        )

        awards: list[PILImage] = []

        for award in allAwards:
            if user and award.data_id not in userCollected:
                awards.append(
                    await drawAwardBox("./res/catch/blank_placeholder.png", "???", "")
                )
            elif user:
                awards.append(
                    await drawAwardBox(
                        await getAwardImage(session, user, award),
                        award.name,
                        "",
                        level.color_code,
                    )
                )
            else:
                awards.append(
                    await drawAwardBox(award.img_path, award.name, "", level.color_code)
                )

        boxes.append(
            await combineABunchOfImage(
                int(10 * GLOBAL_SCALAR),
                int(10 * GLOBAL_SCALAR),
                awards,
                6,
                "#696361",
                "top",
                "left",
            )
        )

    return await verticalPile(
        boxes,
        int(10 * GLOBAL_SCALAR),
        "left",
        "#696361",
        int(80 * GLOBAL_SCALAR),
        int(40 * GLOBAL_SCALAR),
        int(40 * GLOBAL_SCALAR),
        int(40 * GLOBAL_SCALAR),
    )


async def drawCaughtBoxes(session: async_scoped_session, picks: PicksResult):
    boxes: list[PILImage] = []
    user = await picks.dbUser(session)

    for pick in picks.picks:
        award = await pick.dbAward(session)
        level = award.level

        image = await catch(
            award.name,
            await getAwardDescription(session, user, award),
            await getAwardImage(session, user, award),
            level.name,
            level.color_code,
            pick.isNew(),
            f"+{pick.delta}",
        )

        boxes.append(image)

    return await verticalPile(boxes, 33, "left", "#EEEBE3", 80, 80, 80, 80)


driver = get_driver()


@driver.on_startup
async def preDrawEverything():
    if config.predraw_images == 0:
        logger.info("在开发环境中，跳过了预先绘制图像文件")
        return

    session = get_session()

    awards = await getAllAwards(session)
    begin = time.time()

    for ind, award in enumerate(awards):
        bg = award.level.color_code
        await display_box(bg, award.img_path)
        logger.info(f"{ind + 1}/{len(awards)} 预渲染完成了 {award.name}")

    skins = await getAllSkins(session)

    for ind, skin in enumerate(skins):
        bg = skin.award.level.color_code
        await display_box(bg, skin.image)
        logger.info(f"{ind + 1}/{len(skins)} 预渲染完成了 {skin.name}")

    logger.info(f"已经完成了预先绘制图像文件，耗时 {time.time() - begin}")


def getImageTarget(award: Award):
    safename = (
        base64.b64encode(award.name.encode())
        .decode()
        .replace("/", "_")
        .replace("+", "-")
    )

    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "catch", "awards", f"{safename}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    return _path()


def getSkinTarget(skin: Skin):
    safename = (
        base64.b64encode((skin.award.name + skin.name).encode())
        .decode()
        .replace("/", "_")
        .replace("+", "-")
    )

    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "catch", "skins", f"{safename}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    return _path()
