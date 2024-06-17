import os
from nonebot import logger
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.download import download, writeData
from src.models.models import OwnedSkin, Skin, SkinAltName, UsedSkin


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
    query = select(UsedSkin.data_id).filter(UsedSkin.user_id == uid)
    result = await session.execute(query)

    if (res := result.scalar()) is not None:
        query = update(UsedSkin).where(UsedSkin.data_id == res).values(skin_id=sid)
        await session.execute(query)
    else:
        new_skin = UsedSkin(user_id=uid, skin_id=sid)
        session.add(new_skin)
    await session.flush()


async def clear_skin(session: AsyncSession, uid: int):
    query = delete(UsedSkin).filter(UsedSkin.user_id == uid)
    await session.execute(query)


async def get_sid_by_name(session: AsyncSession, name: str):
    query = select(Skin.data_id).filter(Skin.name == name)
    res = (await session.execute(query)).scalar_one_or_none()

    if res is None:
        query = select(Skin.data_id).filter(Skin.alt_names.any(
            SkinAltName.name == name
        ))
        res = (await session.execute(query)).scalar_one_or_none()
    
    return res


async def downloadSkinImage(sid: int, url: str):
    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "skins", f"{sid}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    await writeData(await download(url), _path())

    return _path()
