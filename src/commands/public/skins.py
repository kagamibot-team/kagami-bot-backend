from dataclasses import dataclass
import time
from arclet.alconna import Arg, Alconna, Arparma, ArgFlag
from nonebot import logger
from nonebot_plugin_alconna import UniMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import *

from src.common.classes.command_events import PublicContext
from src.common.decorators.command_decorators import (
    listenPublic,
    matchAlconna,
    requireAdmin,
    withFreeSession,
)


@dataclass
class SkinInfo:
    aName: str
    name: str
    image: str
    extra_description: str
    price: float


@listenPublic()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "re:(所有|全部)皮肤",
        Arg("name", str, flags=[ArgFlag.OPTIONAL]),
    )
)
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    name = res.query[str]("name")

    targ = Award.name, Skin.name, Skin.image, Skin.extra_description, Skin.price

    if name:
        query1 = (
            select(*targ)
            .filter(Skin.award.has(Award.name == name))
            .join(Award, Skin.applied_award_id == Award.data_id)
        )
        query2 = (
            select(*targ)
            .filter(Skin.name == name)
            .join(Award, Skin.applied_award_id == Award.data_id)
        )
        query3 = (
            select(*targ)
            .filter(Skin.award.has(Award.alt_names.any(AwardAltName.name == name)))
            .join(Award, Skin.applied_award_id == Award.data_id)
        )
        query4 = (
            select(*targ)
            .filter(Skin.alt_names.any(SkinAltName.name == name))
            .join(Award, Skin.applied_award_id == Award.data_id)
        )

        begin = time.time()
        skins1 = (await session.execute(query1)).tuples()
        logger.debug(f"查询耗时1: {time.time() - begin}")

        begin = time.time()
        skins2 = (await session.execute(query2)).tuples()
        logger.debug(f"查询耗时2: {time.time() - begin}")

        begin = time.time()
        skins3 = (await session.execute(query3)).tuples()
        logger.debug(f"查询耗时3: {time.time() - begin}")

        begin = time.time()
        skins4 = (await session.execute(query4)).tuples()
        logger.debug(f"查询耗时4: {time.time() - begin}")

        skins = list(skins1) + list(skins2) + list(skins3) + list(skins4)
    else:
        query = select(*targ).join(Award, Skin.applied_award_id == Award.data_id)

        begin = time.time()
        skins = list((await session.execute(query)).tuples())
        logger.debug(f"查询耗时: {time.time() - begin}")

    message = UniMessage().text("所有皮肤：\n")

    if len(skins) < 5:
        for skin in skins:
            skinInfo = SkinInfo(*skin)

            message += f"{skinInfo.aName}[{skinInfo.name}]"
            message += UniMessage().image(path=skinInfo.image)
            message += f"{skinInfo.extra_description}\n\n"
    else:
        for skin in skins:
            skinInfo = SkinInfo(*skin)
            message += (
                f"{skinInfo.aName}[{skinInfo.name}]\n{skinInfo.extra_description}\n\n"
            )

    await ctx.reply(message)
