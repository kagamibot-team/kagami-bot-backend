import os
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.download import download, writeData
from src.models.models import *
from src.common.dataclasses.award_info import AwardInfo


async def get_award_info(session: AsyncSession, uid: int, aid: int):
    query = (
        select(
            Award.data_id,
            Award.img_path,
            Award.name,
            Award.description,
            Level.name,
            Level.color_code,
        )
        .filter(Award.data_id == aid)
        .join(Level, Level.data_id == Award.level_id)
    )
    award = (await session.execute(query)).one().tuple()

    skinQuery = (
        select(Skin.name, Skin.extra_description, Skin.image)
        .filter(Skin.applied_award_id == award[0])
        .filter(Skin.used_skins.any(UsedSkin.user_id == uid))
    )
    skin = (await session.execute(skinQuery)).one_or_none()

    info = AwardInfo(
        awardId=award[0],
        awardImg=award[1],
        awardName=award[2],
        awardDescription=award[3],
        levelName=award[4],
        color=award[5],
        skinName=None,
    )

    if skin:
        skin = skin.tuple()
        info.skinName = skin[0]
        info.awardDescription = (
            skin[1] if len(skin[1].strip()) > 0 else info.awardDescription
        )
        info.awardImg = skin[2]

    return info


async def get_storage(session: AsyncSession, uid: int, aid: int):
    """返回用户库存里有多少小哥

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 uid
        aid (int): 小哥 id

    Returns:
        int: 库存小哥的数量
    """
    query = select(StorageStats.count).filter(
        StorageStats.target_user_id == uid, StorageStats.target_award_id == aid
    )

    return (await session.execute(query)).scalar_one_or_none()


async def get_statistics(session: AsyncSession, uid: int, aid: int):
    """获得迄今为止一共抓到了多少小哥

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户在数据库中的 ID
        aid (int): 小哥在数据库中的 ID
    """

    query1 = select(StorageStats.count).filter(
        StorageStats.target_user_id == uid, StorageStats.target_award_id == aid
    )
    query2 = select(UsedStats.count).filter(
        UsedStats.target_user_id == uid, UsedStats.target_award_id == aid
    )

    sto = (await session.execute(query1)).scalar_one_or_none() or 0
    use = (await session.execute(query2)).scalar_one_or_none() or 0

    return sto + use


async def add_storage(session: AsyncSession, uid: int, aid: int, count: int):
    """增减一个用户的小哥库存

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 ID
        aid (int): 小哥 ID
        count (int): 增减数量。如果值小于 0，会记录使用的量。

    Returns:
        int: 在调整库存之前，用户的库存值
    """
    res = await get_storage(session, uid, aid)

    if res is None:
        newStorage = StorageStats(target_user_id=uid, target_award_id=aid, count=count)
        session.add(newStorage)
        return 0

    query = (
        update(StorageStats)
        .where(
            StorageStats.target_user_id == uid,
            StorageStats.target_award_id == aid,
        )
        .values(count=res + count)
    )
    await session.execute(query)

    if count < 0:
        query = (
            update(UsedStats)
            .where(UsedStats.target_award_id == aid, UsedStats.target_user_id == uid)
            .values(count=UsedStats.count - count)
        )

    return res


async def get_aid_by_name(session: AsyncSession, name: str):
    query = select(Award.data_id).filter(Award.name == name)
    res = (await session.execute(query)).scalar_one_or_none()

    if res is None:
        query = select(Award.data_id).filter(
            Award.alt_names.any(AwardAltName.name == name)
        )
        res = (await session.execute(query)).scalar_one_or_none()

    return res


async def download_award_image(aid: int, url: str):
    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "awards", f"{aid}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    await writeData(await download(url), _path())

    return _path()
