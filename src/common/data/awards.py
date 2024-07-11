import os

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.event_root import root
from src.common.data.skins import get_using_skin
from src.common.dataclasses.award_info import AwardInfo
from src.common.dataclasses.data_changed_events import PlayerStorageChangedEvent
from src.common.download import download, writeData
from src.models.models import *
from src.models.statics import level_repo


async def get_award_info(session: AsyncSession, uid: int, aid: int):
    query = select(
        Award.data_id,
        Award.image,
        Award.name,
        Award.description,
        Award.level_id,
    ).filter(Award.data_id == aid)
    award = (await session.execute(query)).one().tuple()

    using_skin = await get_using_skin(session, uid, aid)
    skin = None
    if using_skin is not None:
        query = select(Skin.name, Skin.description, Skin.image).filter(
            Skin.data_id == using_skin
        )
        skin = (await session.execute(query)).one_or_none()

    level = level_repo.levels[award[4]]

    info = AwardInfo(
        awardId=award[0],
        awardImg=award[1],
        awardName=award[2],
        awardDescription=award[3],
        levelName=level.display_name,
        color=level.color,
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
    query = select(Inventory.storage).filter(
        Inventory.user_id == uid, Inventory.award_id == aid
    )

    return (await session.execute(query)).scalar_one_or_none()


async def get_statistics(session: AsyncSession, uid: int, aid: int):
    """获得迄今为止一共抓到了多少小哥

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户在数据库中的 ID
        aid (int): 小哥在数据库中的 ID
    """

    query = select(Inventory.storage, Inventory.used).filter(
        Inventory.user_id == uid, Inventory.award_id == aid
    )

    sto, use = (await session.execute(query)).tuples().one_or_none() or (0, 0)

    return sto + use


async def give_award(session: AsyncSession, uid: int, aid: int, count: int):
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
        newStorage = Inventory(user_id=uid, award_id=aid, storage=count)
        session.add(newStorage)
        await session.flush()
        return 0

    query = (
        update(Inventory)
        .where(Inventory.user_id == uid, Inventory.award_id == aid)
        .values(storage=res + count)
    )
    await session.execute(query)

    if count < 0:
        query = (
            update(Inventory)
            .where(Inventory.user_id == uid, Inventory.award_id == aid)
            .values(used=Inventory.used + count)
        )

    # 释放相关的事件
    await root.emit(PlayerStorageChangedEvent(uid, aid, count, res, res + count))

    return res


async def get_aid_by_name(session: AsyncSession, name: str):
    query = select(Award.data_id).filter(Award.name == name)
    res = (await session.execute(query)).scalar_one_or_none()

    if res is None:
        query = (
            select(Award.data_id)
            .join(AwardAltName, AwardAltName.award_id == Award.data_id)
            .filter(AwardAltName.name == name)
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
