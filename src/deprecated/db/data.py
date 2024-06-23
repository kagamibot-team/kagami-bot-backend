"""
`data` 模块主要用于数据的基本修改，在这里实现一些修改数据库数据的基本逻辑。

未来需要实现，将该模块中所有对数据库的操作全部转移至 `curd` 中。
"""

import time
from typing import cast
from nonebot import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models import *

from .crud import *



Session = AsyncSession


async def setInterval(session: Session, interval: float):
    "设置全局的抓小哥周期"

    await session.execute(update(User).values(pick_time_delta=interval))
    glob = await getGlobal(session)
    glob.catch_interval = interval


async def giveAward(session: Session, user: User, award: Award, delta: int) -> int:
    "给予玩家小哥，返回数据库中原先的值"

    aws = await getStorage(session, user, award)
    aws.count += delta

    return aws.count - delta


async def reduceAward(session: Session, user: User, award: Award, count: int) -> bool:
    "减少玩家的小哥量，返回是否成功"

    record = await getStorage(session, user, award)

    if record.count < count:
        return False

    record.count -= count
    stats = await getUsed(session, user, award)
    stats.count += count
    return True


async def getPosibilities(session: Session, level: Level):
    begin = time.time()
    levels = (await session.execute(select(Level.weight))).scalars()
    weightSum = sum(levels)
    logger.debug("获取所有等级耗时：%f" % (time.time() - begin))

    return level.weight / weightSum


async def obtainSkin(session: Session, user: User, skin: Skin):
    record = await getOwnedSkin(session, user, skin)

    if record is not None:
        return False

    record = OwnedSkin(
        user=user,
        skin=skin,
    )

    session.add(record)
    await session.flush()
    return True


async def deleteSkinOwnership(session: Session, user: User, skin: Skin):
    record = await getOwnedSkin(session, user, skin)

    if record is None:
        return False

    await session.delete(record)

    usingRecord = (
        await session.execute(
            select(UsedSkin).filter(UsedSkin.user == user).filter(UsedSkin.skin == skin)
        )
    ).scalar_one_or_none()

    if usingRecord is not None:
        await session.delete(usingRecord)

    return True


async def switchSkin(
    session: Session, user: User, skins: list[Skin], award: Award
) -> Skin | None:
    usingRecord = await getUsedSkin(session, user, award)

    if usingRecord is None:
        usingRecord = UsedSkin(
            user=user,
            skin=skins[0],
        )
        session.add(usingRecord)
        await session.flush()
        return skins[0]

    if usingRecord.skin not in skins:
        usingRecord.skin = skins[0]

        logger.warning(
            f"[WARNING] 用户 {user.data_id} 切换了皮肤，但是没有找到对应的皮肤，已切换为第一个皮肤"
        )
        return skins[0]

    index = skins.index(usingRecord.skin)

    if index == len(skins) - 1:
        await session.delete(usingRecord)
        return None

    usingRecord.skin = skins[index + 1]
    return skins[index + 1]


async def resetCacheCount(session: Session, count: int):
    await session.execute(update(User).values(pick_max_cache=count))


async def getUserStorages(session: Session, user: User):
    "获得一个用户在库存页上展示的全部库存统计"

    return (
        (
            await session.execute(
                select(StorageStats)
                .filter(StorageStats.user == user)
                .filter(StorageStats.count > 0)
                .join(Award, StorageStats.award)
                .join(Level, Award.level)
                .order_by(
                    -Level.sorting_priority,
                    Level.weight,
                    -StorageStats.count,
                    Award.data_id,
                )
            )
        )
        .scalars()
        .all()
    )


async def getUserStoragesByLevel(session: Session, user: User, level: Level):
    _query = (
        select(StorageStats.target_award_id)
        .filter(StorageStats.user == user)
        .join(Award, StorageStats.award)
        .filter(Award.level == level)
    )
    return (await session.execute(_query)).scalars().all()


class AwardInfo(BaseModel):
    awardId: int
    awardImg: str
    awardName: str
    awardDescription: str
    levelName: str
    color: str
    skinName: str | None


async def GetAwardInfo(session: Session, user: User, award: Award):
    begin = time.time()
    record = await getUsedSkin(session, user, award)
    logger.debug("获取皮肤记录花了 %.3f 秒" % (time.time() - begin))

    desc = award.description
    img = award.img_path
    sName = None

    if record is not None and len(desc.strip()) > 0:
        desc = record.skin.extra_description
    
    if record is not None:
        img = record.skin.image
        sName = record.skin.name

    return AwardInfo(
        awardId=cast(int, award.data_id),
        awardImg=img,
        awardName=award.name,
        awardDescription=desc,
        levelName=award.level.name,
        color=award.level.color_code,
        skinName=sName,
    )
    

async def buy(session: AsyncSession, user: User, code: str, price: float):
    user.money -= price

    if code == "加上限":
        user.pick_max_cache += 1
        return

    if len(code) > 2 and code[:2] == "皮肤":
        skinName = code[2:]
        skin = await getSkinByName(session, skinName)
        assert skin is not None
        await obtainSkin(session, user, skin)
        return


__all__ = [
    "setInterval",
    "giveAward",
    "reduceAward",
    "getPosibilities",
    "obtainSkin",
    "deleteSkinOwnership",
    "switchSkin",
    "resetCacheCount",
    "getUserStorages",
    "getUserStoragesByLevel",
    "buy",
]
