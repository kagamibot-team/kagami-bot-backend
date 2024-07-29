import os

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.download import download, writeData
from src.models.models import Skin, SkinRecord


async def give_skin(session: AsyncSession, uid: int, sid: int):
    """给予玩家皮肤。如果玩家已经有了，则跳过

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 ID
        sid (int): 皮肤 ID
    """
    query = select(SkinRecord.data_id).filter(
        SkinRecord.user_id == uid, SkinRecord.skin_id == sid
    )
    result = await session.execute(query)

    if result.scalar() is None:
        new_skin = SkinRecord(user_id=uid, skin_id=sid)
        session.add(new_skin)
        await session.flush()


async def use_skin(session: AsyncSession, uid: int, sid: int):
    """让某个用户挂载皮肤。如果用户没有那个皮肤，则不会有反应。

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 ID
        sid (int): 皮肤 ID
    """
    query = select(Skin.award_id).filter(Skin.data_id == sid)
    _aid = (await session.execute(query)).scalar_one()
    await unuse_all_skins(session, uid, _aid)
    query = (
        update(SkinRecord)
        .where(SkinRecord.skin_id == sid, SkinRecord.user_id == uid)
        .values({SkinRecord.selected: 1})
    )
    await session.execute(query)


async def unuse_all_skins(session: AsyncSession, uid: int, aid: int):
    """让用户取消挂载某个小哥的所有皮肤

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 ID
        sid (int): 小哥 ID
    """
    query = (
        update(SkinRecord)
        .where(
            SkinRecord.user_id == uid,
            Skin.data_id == SkinRecord.skin_id,
            Skin.award_id == aid,
        )
        .values({SkinRecord.selected: 0})
    )
    await session.execute(query)


async def downloadSkinImage(sid: int, url: str):
    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "skins", f"{sid}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    await writeData(await download(url), _path())

    return _path()
