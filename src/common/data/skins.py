import os

from nonebot import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import MultipleResultsFound

from src.common.download import download, writeData
from src.common.lang.zh import la
from src.models.models import Skin, SkinAltName, SkinRecord


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


async def do_user_have_skin(session: AsyncSession, uid: int, sid: int):
    """判断玩家是否有某个皮肤

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 ID
        sid (int): 皮肤 ID

    Returns:
        bool: 是否拥有某个皮肤
    """
    query = select(SkinRecord.data_id).filter(
        SkinRecord.user_id == uid, SkinRecord.skin_id == sid
    )
    result = await session.execute(query)

    return result.scalar() is not None


async def get_using_skin(session: AsyncSession, uid: int, aid: int):
    """获得用户某个小哥正在使用的皮肤。如果没有使用，则返回 None。

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 ID
        aid (int): 小哥 ID

    Returns:
        int | None: 使用的皮肤的 ID
    """
    try:
        query = (
            select(Skin.data_id)
            .join(SkinRecord, Skin.data_id == SkinRecord.skin_id)
            .filter(SkinRecord.user_id == uid, SkinRecord.selected == 1)
            .filter(Skin.award_id == aid)
        )
        result = await session.execute(query)

        return result.scalar_one_or_none()
    except MultipleResultsFound as e:
        logger.warning(e)
        return None


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
        .values(selected=1)
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
        .values(selected=0)
    )
    await session.execute(query)


async def get_sid_by_name(session: AsyncSession, name: str):
    """根据名字筛选皮肤的 ID

    Args:
        session (AsyncSession): 数据库会话
        name (str): 名字

    Returns:
        int: 皮肤 ID
    """
    query = select(Skin.data_id).filter(Skin.name == name)
    res = (await session.execute(query)).scalar_one_or_none()

    if res is None:
        query = (
            select(Skin.data_id)
            .join(SkinAltName, SkinAltName.skin_id == Skin.data_id)
            .filter(SkinAltName.name == name)
        )
        res = (await session.execute(query)).scalar_one_or_none()

    return res


async def switch_skin_of_award(session: AsyncSession, uid: int, aid: int):
    """切换到下一个皮肤。如果已经是最后一个，则取消选中皮肤

    Args:
        session (AsyncSession): 数据库会话
        user (int): 用户 ID
        aid (int): 小哥 ID

    Returns:
        int | None: 应用上的小哥皮肤 ID
    """
    query = (
        select(SkinRecord.skin_id)
        .join(Skin, SkinRecord.skin_id == Skin.data_id)
        .filter(SkinRecord.user_id == uid)
        .filter(Skin.award_id == aid)
    )
    skins = (await session.execute(query)).scalars().all()

    if len(skins) == 0:
        return None

    using = await get_using_skin(session, uid, aid)

    if using is None:
        await use_skin(session, uid, skins[0])
        return skins[0]

    for i, id in enumerate(skins):
        if id == using:
            if i == len(skins) - 1:
                await unuse_all_skins(session, uid, aid)
                return None

            await use_skin(session, uid, skins[i + 1])
            return skins[i + 1]

    logger.warning(la.warn.log_use_skin_not_exists.format(uid))
    await unuse_all_skins(session, uid, aid)
    return None


async def get_skin_name(session: AsyncSession, sid: int):
    query = select(Skin.name).filter(Skin.data_id == sid).limit(1)
    return (await session.execute(query)).scalar_one()


async def downloadSkinImage(sid: int, url: str):
    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "skins", f"{sid}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    await writeData(await download(url), _path())

    return _path()
