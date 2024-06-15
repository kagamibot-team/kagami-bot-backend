import pathlib
from nonebot_plugin_alconna import Alconna, Arparma, UniMessage
from arclet.alconna import Arg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import (
    Award,
    AwardAltName,
    Level,
    Skin,
    StorageStats,
    UsedSkin,
    UsedStats,
)

from src.db.data import AwardInfo

from src.db.crud import getUser

from src.events.context import OnebotContext
from src.events import root
from src.events.decorator import listenOnebot, matchAlconna, withSessionLock


@listenOnebot()
@matchAlconna(Alconna("re:(展示|zhanshi|zs)", Arg("name", str)))
@withSessionLock()
async def _(ctx: OnebotContext, session: AsyncSession, result: Arparma):
    name = result.query[str]("name")
    user = await getUser(session, ctx.getSenderId())

    if name is None:
        return

    target = (
        Award.data_id,
        Award.img_path,
        Award.name,
        Award.description,
        Level.name,
        Level.color_code,
    )

    query1 = (
        select(*target)
        .join(Level, Level.data_id == Award.level_id)
        .filter(Award.name == name)
    )
    award = (await session.execute(query1)).one_or_none()

    if award is None:
        query2 = (
            select(*target)
            .join(Level, Level.data_id == Award.level_id)
            .filter(Award.alt_names.any(AwardAltName.name == name))
        )
        award = (await session.execute(query2)).one_or_none()

    if award is None:
        await ctx.reply(UniMessage(f"没有叫 {name} 的小哥"))
        return

    award = award.tuple()

    ac = (
        await session.execute(
            select(StorageStats.count)
            .filter(StorageStats.user == user)
            .filter(StorageStats.target_award_id == award[0])
        )
    ).scalar_one_or_none() or 0
    au = (
        await session.execute(
            select(UsedStats.count)
            .filter(UsedStats.user == user)
            .filter(UsedStats.target_award_id == award[0])
        )
    ).scalar_one_or_none() or 0

    if ac + au <= 0:
        await ctx.reply(UniMessage(f"你还没有遇到过叫做 {name} 的小哥"))
        return

    skinQuery = (
        select(Skin.name, Skin.extra_description, Skin.image)
        .filter(Skin.applied_award_id == award[0])
        .filter(Skin.used_skins.any(UsedSkin.user == user))
    )
    skin = (await session.execute(skinQuery)).one_or_none()

    info = AwardInfo(
        awardId=award[0],
        awardImg=award[1],
        awardName=award[2],
        awardDescription=award[3],
        levelName=award[4],
        color=award[5],
        skinName=None,
    )

    if skin:
        skin = skin.tuple()
        info.skinName = skin[0]
        info.awardDescription = (
            skin[1] if len(skin[1].strip()) > 0 else info.awardDescription
        )
        info.awardImg = skin[2]

    nameDisplay = info.awardName

    if info.skinName is not None:
        nameDisplay += f"[{info.skinName}]"

    await ctx.reply(
        UniMessage()
        .text(nameDisplay + f"【{info.levelName}】")
        .image(path=pathlib.Path(info.awardImg))
        .text(f"\n\n{info.awardDescription}")
    )
