"""
`curd` 模块主要用于数据库的增、删、查、改。任何逻辑都不应该在这里实现。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from src.models import *


Session = AsyncSession


async def deleteObj(session: Session, obj: object):
    "删除对象"

    if obj is None:
        return

    await session.delete(obj)
    await session.flush()


async def getAwardByName(session: Session, name: str):
    "根据名字返回小哥，如果不存在则返回 None"

    award = (
        await session.execute(select(Award).filter(Award.name == name))
    ).scalar_one_or_none()

    if award is None:
        awardAlt = (
            await session.execute(
                select(AwardAltName).filter(AwardAltName.name == name)
            )
        ).scalar_one_or_none()
        if awardAlt is not None:
            award = await session.get(Award, awardAlt.award_id)

    return award


async def createAwardAltName(session: Session, award: Award, name: str):
    "创建一个小哥的别名，返回是否创建成功"

    _a = await getAwardByName(session, name)

    if _a is not None:
        return False

    alt = AwardAltName(award=award, name=name)
    session.add(alt)
    await session.flush()

    return True


async def getAwardAltNameObject(session: Session, name: str):
    "根据名字返回小哥的别名，如果不存在则返回 None"

    return (
        await session.execute(select(AwardAltName).filter(AwardAltName.name == name))
    ).scalar_one_or_none()


### USER ###
async def getUser(session: Session, qqid: int):
    "返回一个用户，如果该用户不存在，则立即创建"

    userResult = await session.execute(
        select(User)
        .with_hint(User, "USE INDEX ix_catch_user_data_qq_id")
        .filter(User.qq_id == str(qqid))
    )

    user = userResult.scalar_one_or_none()

    if user is None:
        user = User(qq_id=str(qqid))
        session.add(user)
        await session.flush()

    return user


async def getInventory(session: Session, user: User, award: Award):
    "返回一个用户的小哥库存，如果没有，则立即创建"

    stats = (
        await session.execute(
            select(Inventory)
            .filter(Inventory.user_id == user.data_id)
            .filter(Inventory.award_id == award.data_id)
        )
    ).scalar_one_or_none()

    if not stats:
        stats = Inventory(user=user, award=award, count=0)
        session.add(stats)

    return stats


async def getSkinByName(session: Session, name: str):
    "根据名字返回皮肤，如果没有则返回 None"

    skin = (
        await session.execute(select(Skin).filter(Skin.name == name))
    ).scalar_one_or_none()

    if skin is None:
        skinAlt = (
            await session.execute(select(SkinAltName).filter(SkinAltName.name == name))
        ).scalar_one_or_none()
        if skinAlt is not None:
            skin = await session.get(Skin, skinAlt.skin_id)

    return skin


async def createSkinAltName(session: Session, skin: Skin, name: str):
    "创建一个皮肤的别名，返回是否创建成功"

    _s = await getSkinByName(session, name)

    if _s is not None:
        return False

    alt = SkinAltName(skin=skin, name=name)
    session.add(alt)
    await session.flush()

    return True


async def getSkinAltNameObject(session: Session, name: str):
    "根据名字返回皮肤的别名，如果不存在则返回 None"

    return (
        await session.execute(select(SkinAltName).filter(SkinAltName.name == name))
    ).scalar_one_or_none()
