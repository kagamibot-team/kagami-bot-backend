from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import OwnedSkin, UsedSkin


async def give_skin(session: AsyncSession, uid: int, sid: int):
    query = select(OwnedSkin.data_id).filter(
        OwnedSkin.user_id == uid, OwnedSkin.skin_id == sid
    )
    result = await session.execute(query)

    if result.scalar() is None:
        new_skin = OwnedSkin(user_id=uid, skin_id=sid)
        session.add(new_skin)


async def set_skin(session: AsyncSession, uid: int, sid: int):
    query = select(UsedSkin.data_id).filter(UsedSkin.user_id == uid)
    result = await session.execute(query)

    if (res := result.scalar()) is not None:
        query = update(UsedSkin).where(UsedSkin.data_id == res).values(skin_id=sid)
        await session.execute(query)
    else:
        new_skin = UsedSkin(user_id=uid, skin_id=sid)
        session.add(new_skin)


async def clear_skin(session: AsyncSession, uid: int):
    query = delete(UsedSkin).filter(UsedSkin.user_id == uid)
    await session.execute(query)
