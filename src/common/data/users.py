from typing import cast
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User


async def get_uid_by_qqid(session: AsyncSession, qqid: int | str):
    qqid = str(qqid)

    result = await session.execute(select(User.data_id).where(User.qq_id == qqid))
    data_id = result.scalar()

    if data_id is None:
        user = User(qq_id=qqid)
        session.add(user)
        await session.flush()
        data_id = cast(int, user.data_id)

    return data_id


async def get_qqid_by_uid(session: AsyncSession, data_id: int | str):
    data_id = str(data_id)

    result = await session.execute(select(User.qq_id).where(User.data_id == data_id))
    qq_id = result.scalar_one()
    
    return qq_id
