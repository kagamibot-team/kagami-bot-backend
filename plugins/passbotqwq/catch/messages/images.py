import base64
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

from ..cores import Pick, PicksResult

from ..models.crud import (
    getAwardDescriptionOfOneUser,
    getAwardImageOfOneUser,
)
from ..models.Basics import Award, AwardCountStorage, AwardSkin, Level, UserData

from ...putils.draw.images import (
    addUponPaste,
    horizontalPile,
    verticalPile,
    combineABunchOfImage,
)
from ...putils.draw.texts import (
    VerticalAnchor,
    drawABoxOfText,
    drawLimitedBoxOfText,
    drawText,
    textFont,
    Fonts,
)
from ...putils.draw.typing import PILImage
from ...putils.draw import newImage

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
                    Fonts.FONT_HARMONYOS_SANS,
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
        textFont(Fonts.FONT_HARMONYOS_SANS_BLACK, int(27 * GLOBAL_SCALAR)),
        strokeColor="#000000",
        strokeWidth=int(2 * GLOBAL_SCALAR),
        verticalAlign=VerticalAnchor.bottom,
    )

    return base


async def drawStorage(session: async_scoped_session, user: UserData):
    awards: list[PILImage] = []

    acs = (
        await session.execute(
            select(AwardCountStorage)
            .filter(AwardCountStorage.target_user == user)
            .filter(AwardCountStorage.award_count > 0)
            .join(Award, AwardCountStorage.target_award)
            .join(Level, Award.level)
            .order_by(
                Level.weight,
                -AwardCountStorage.award_count,
                Award.data_id,
            )
        )
    ).scalars()

    for ac in acs:
        award = ac.target_award
        count = ac.award_count

        awards.append(
            await refBookBox(
                award.name,
                str(count),
                award.level.level_color_code,
                await getAwardImageOfOneUser(session, user, award),
            )
        )

    return await combineABunchOfImage(
        0, 0, awards, 6, "#9B9690", "top", "left", 30, 30, 60, 30
    )


@deprecated("Use images.components.display_box instead")
async def drawAwardBoxImageHidden():
    return await drawAwardBoxImage("./res/catch/blank_placeholder.png")


async def drawStatus(session: async_scoped_session, user: UserData | None):
    boxes: list[PILImage] = []
    levels = (
        (
            await session.execute(
                select(Level).filter(Level.awards.any()).order_by(Level.weight)
            )
        )
        .scalars()
        .all()
    )

    for level in levels:
        allAwards = (
            (
                await session.execute(
                    select(Award).filter(Award.level == level).order_by(Award.data_id)
                )
            )
            .scalars()
            .all()
        )

        if user:
            _query = (
                select(AwardCountStorage.target_award_id)
                .filter(AwardCountStorage.target_user == user)
                .join(Award, AwardCountStorage.target_award)
                .filter(Award.level == level)
            )
            userCollected = list((await session.execute(_query)).scalars())
            title = f"{level.name}：{len(userCollected)} / {len(allAwards)}"
        else:
            userCollected = []
            title = level.name

        boxes.append(
            await drawABoxOfText(
                title,
                level.level_color_code,
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
                        await getAwardImageOfOneUser(session, user, award),
                        award.name,
                        "",
                        level.level_color_code,
                    )
                )
            else:
                awards.append(
                    await drawAwardBox(
                        award.img_path, award.name, "", level.level_color_code
                    )
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

    for pick in picks.picks:
        award = await session.get_one(Award, pick.award)
        user = await session.get_one(UserData, pick.picks.udid)
        level = award.level

        image = await catch(
            award.name,
            await getAwardDescriptionOfOneUser(session, user, award),
            await getAwardImageOfOneUser(session, user, award),
            level.name,
            level.level_color_code,
            pick.isNew(),
            f"+{pick.delta}",
        )

        boxes.append(image)

    return await verticalPile(boxes, 33, "left", "#EEEBE3", 80, 80, 80, 80)


driver = get_driver()


@driver.on_startup
async def preDrawEverything():
    if nonebot.get_driver().config.predraw_images == 0:
        logger.info("在开发环境中，跳过了预先绘制图像文件")
        return

    session = get_session()
    awards = (await session.execute(select(Award))).scalars().all()
    begin = time.time()

    for ind, award in enumerate(awards):
        bg = award.level.level_color_code
        await display_box(bg, award.img_path)
        logger.info(f"{ind + 1}/{len(awards)} 预渲染完成了 {award.name}")

    skins = (await session.execute(select(AwardSkin))).scalars().all()

    for ind, skin in enumerate(skins):
        bg = skin.applied_award.level.level_color_code
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


def getSkinTarget(skin: AwardSkin):
    safename = (
        base64.b64encode((skin.applied_award.name + skin.name).encode())
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
