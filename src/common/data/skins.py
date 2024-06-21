import os
from nonebot import logger
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.download import download, writeData
from src.models.models import OwnedSkin, Skin, SkinAltName, UsedSkin
from sqlalchemy.exc import MultipleResultsFound
from src.common.lang.zh import la


async def give_skin(session: AsyncSession, uid: int, sid: int):
    query = select(OwnedSkin.data_id).filter(
        OwnedSkin.user_id == uid, OwnedSkin.skin_id == sid
    )
    result = await session.execute(query)

    if result.scalar() is None:
        new_skin = OwnedSkin(user_id=uid, skin_id=sid)
        session.add(new_skin)
        await session.flush()


async def set_skin(session: AsyncSession, uid: int, sid: int):
    query = select(Skin.applied_award_id).filter(Skin.data_id == sid)
    _aid = (await session.execute(query)).scalar_one()

    query = (
        select(UsedSkin.data_id)
        .filter(UsedSkin.user_id == uid)
        .join(Skin, Skin.data_id == UsedSkin.skin_id)
        .filter(Skin.applied_award_id == _aid)
    )
    result = await session.execute(query)

    if (res := result.scalar()) is not None:
        query = update(UsedSkin).where(UsedSkin.data_id == res).values(skin_id=sid)
        await session.execute(query)
    else:
        new_skin = UsedSkin(user_id=uid, skin_id=sid)
        session.add(new_skin)
    await session.flush()


async def clear_skin(session: AsyncSession, uid: int, aid: int):
    query = (
        select(UsedSkin.data_id)
        .filter(UsedSkin.user_id == uid)
        .join(Skin, Skin.data_id == UsedSkin.skin_id)
        .filter(Skin.applied_award_id == aid)
    )
    dt = (await session.execute(query)).scalars().all()

    query = delete(UsedSkin).where(UsedSkin.data_id.in_(dt))
    await session.execute(query)


async def get_sid_by_name(session: AsyncSession, name: str):
    query = select(Skin.data_id).filter(Skin.name == name)
    res = (await session.execute(query)).scalar_one_or_none()

    if res is None:
        query = select(Skin.data_id).filter(
            Skin.alt_names.any(SkinAltName.name == name)
        )
        res = (await session.execute(query)).scalar_one_or_none()

    return res


async def switch_skin_of_award(session: AsyncSession, user: int, aid: int):
    query = (
        select(OwnedSkin.skin_id, Skin.name)
        .join(Skin, OwnedSkin.skin_id == Skin.data_id)
        .filter(OwnedSkin.user_id == user)
        .filter(Skin.applied_award_id == aid)
    )
    skins = (await session.execute(query)).tuples().all()

    if len(skins) == 0:
        return None

    query = (
        select(UsedSkin.skin_id)
        .filter(UsedSkin.user_id == user)
        .join(Skin, UsedSkin.skin_id == Skin.data_id)
        .filter(Skin.applied_award_id == aid)
    )

    try:
        used = (await session.execute(query)).one_or_none()
    except MultipleResultsFound:
        logger.warning(la.warn.log_multi_skin.format(user))
        await clear_skin(session, user, aid)
        return None

    if used is None:
        await set_skin(session, user, skins[0][0])
        return skins[0]

    for i, (id, _) in enumerate(skins):
        if id == used[0]:
            if i == len(skins) - 1:
                await clear_skin(session, user, aid)
                return None

            await set_skin(session, user, skins[i + 1][0])
            return skins[i + 1]

    logger.warning(la.warn.log_use_skin_not_exists.format(user))
    await clear_skin(session, user, aid)
    return None


async def downloadSkinImage(sid: int, url: str):
    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "skins", f"{sid}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    await writeData(await download(url), _path())

    return _path()
