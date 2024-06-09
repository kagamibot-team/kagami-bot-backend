import base64
import os
import PIL
import PIL.ImageDraw

import PIL.ImageFont
import nonebot
from sqlalchemy import select
from nonebot.log import logger
from nonebot_plugin_orm import async_scoped_session, get_session
from nonebot import get_driver

from ..cores import Pick

from ..models.crud import (
    getAwardImageOfOneUser,
)
from ..models.Basics import Award, AwardCountStorage, AwardSkin, Level, UserData

from ...putils.draw.images import (
    addUponPaste,
    loadImage,
    resize,
    horizontalPile,
    verticalPile,
    combineABunchOfImage,
)
from ...putils.draw.texts import (
    HorizontalAnchor,
    VerticalAnchor,
    drawABoxOfText,
    drawLimitedBoxOfText,
    drawText,
    textFont,
    Fonts,
)
from ...putils.draw.typing import PILImage
from ...putils.draw import newImage


GLOBAL_SCALAR = 1.5


__cached_box_image: dict[tuple[str, str], PILImage] = {}


async def drawAwardBoxImage(awardURL: str, background: str = "#9e9d95"):
    _key = (awardURL, background)

    if _key in __cached_box_image:
        return __cached_box_image[_key]

    base = await newImage((int(120 * GLOBAL_SCALAR), int(96 * GLOBAL_SCALAR)), background)
    await addUponPaste(base, await resize(await loadImage(awardURL), int(120 * GLOBAL_SCALAR), int(96 * GLOBAL_SCALAR)), 0, 0)

    __cached_box_image[_key] = base
    return base


async def drawAwardBox(
    awardURL: str, awardName: str, count: str, background: str = "#9e9d95"
):
    base = await verticalPile(
        [
            await drawAwardBoxImage(awardURL, background),
            await drawLimitedBoxOfText(
                awardName,
                int(120 * GLOBAL_SCALAR),
                "center",
                "center",
                int(18 * GLOBAL_SCALAR),
                background,
                textFont(Fonts.FONT_HARMONYOS_SANS, int(14 * GLOBAL_SCALAR)),
            ),
        ],
        int(3 * GLOBAL_SCALAR),
        "center",
        "#696361",
    )

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
                -Level.weight,
                -AwardCountStorage.award_count,
                Award.data_id,
            )
        )
    ).scalars()

    for ac in acs:
        award = ac.target_award
        count = ac.award_count

        awards.append(
            await drawAwardBox(
                await getAwardImageOfOneUser(session, user, award),
                award.name,
                str(count),
                award.level.level_color_code,
            )
        )

    return await combineABunchOfImage(
        int(10 * GLOBAL_SCALAR), int(10 * GLOBAL_SCALAR), awards, 6, "#696361", "top", "left", int(30 * GLOBAL_SCALAR), int(30 * GLOBAL_SCALAR), int(60 * GLOBAL_SCALAR), int(30 * GLOBAL_SCALAR)
    )


async def drawAwardBoxImageHidden():
    return await drawAwardBoxImage("./res/catch/blank_placeholder.png")


async def drawStatus(session: async_scoped_session, user: UserData | None):
    boxes: list[PILImage] = []
    levels = (
        (
            await session.execute(
                select(Level).filter(Level.awards.any()).order_by(-Level.weight)
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
                awards.append(await drawAwardBoxImageHidden())
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
                int(10 * GLOBAL_SCALAR), int(10 * GLOBAL_SCALAR), awards, 6, "#696361", "top", "left"
            )
        )

    return await verticalPile(boxes, int(10 * GLOBAL_SCALAR), "left", "#696361", int(80 * GLOBAL_SCALAR), int(40 * GLOBAL_SCALAR), int(40 * GLOBAL_SCALAR), int(40 * GLOBAL_SCALAR))


async def drawCaughtBox(session: async_scoped_session, pick: Pick):
    award = await session.get_one(Award, pick.award)
    user = await session.get_one(UserData, pick.picks.udid)

    bg = award.level.level_color_code
    imgUrl = await getAwardImageOfOneUser(session, user, award)

    return await drawAwardBox(
        imgUrl, award.name, f"{pick.fromNumber}→{pick.toNumber}", bg
    )


driver = get_driver()


@driver.on_startup
async def preDrawEverything():
    if nonebot.get_driver().config.predraw_images == 0:
        logger.info("在开发环境中，跳过了预先绘制图像文件")
        return

    session = get_session()
    awards = (await session.execute(select(Award))).scalars()

    for award in awards:
        bg = award.level.level_color_code
        await drawAwardBoxImage(award.img_path, bg)

    logger.info("已经完成了预先绘制图像文件")


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
        return os.path.join(".", "data", "catch", "awards", f"{safename}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    return _path()
