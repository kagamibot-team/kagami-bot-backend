from typing import cast
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User


async def get_uid_by_qqid(session: AsyncSession, qqid: int | str):
    """根据用户的 QQ 号获得在数据库中的 UID，如果数据库中没有用户信息，会创建一个数据库行

    Args:
        session (AsyncSession): 数据库会话
        qqid (int | str): QQ 号

    Returns:
        int: 获得用户的数据库 ID
    """
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


async def get_user_money(session: AsyncSession, uid: int) -> float:
    return (
        await session.execute(select(User.money).filter(User.data_id == uid))
    ).scalar_one()


async def set_user_money(session: AsyncSession, uid: int, money: float):
    await session.execute(update(User).where(User.data_id == uid).values(money=money))
