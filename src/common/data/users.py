from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User


async def get_user_flags(session: AsyncSession, uid: int) -> set[str]:
    return set(
        (await session.execute(select(User.feature_flag).filter(User.data_id == uid)))
        .scalar_one()
        .split(",")
    )


async def set_user_flags(session: AsyncSession, uid: int, flags: set[str]):
    await session.execute(
        update(User).where(User.data_id == uid).values(feature_flag=",".join(flags))
    )


async def do_user_have_flag(session: AsyncSession, uid: int, flag: str) -> bool:
    flags = await get_user_flags(session, uid)
    return flag in flags


async def add_user_flag(session: AsyncSession, uid: int, flag: str):
    flags = await get_user_flags(session, uid)
    flags.add(flag)

    await set_user_flags(session, uid, flags)
