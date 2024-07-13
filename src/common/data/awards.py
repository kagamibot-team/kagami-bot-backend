"""
该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息
"""

import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import deprecated

from src.base.exceptions import LackException
from src.common.data.skins import get_using_skin
from src.common.dataclasses.award_info import AwardInfoDeprecated as AwardInfoDeprecated
from src.common.download import download, writeData
from src.common.draw.strange import make_strange
from src.common.draw.tools import imageToBytes
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork
from src.models.models import *
from src.models.statics import level_repo
from src.repositories.inventory_repository import InventoryRepository
from src.views.award import AwardInfo


async def uow_get_award_info(uow: UnitOfWork, aid: int, uid: int | None = None):
    """在大规模重构之前提供的临时方法，用来获取一个小哥的基础信息

    Args:
        uow (UnitOfWork): 工作单元
        aid (int): 小哥 ID
        uid (int | None, optional): 用户 ID，可留空，用来获取皮肤的信息. Defaults to None.
    """
    aname, desc, lid, img = await uow.awards.get_info(aid)
    level = uow.levels.get_by_id(lid)
    sname = None
    sid = None

    if uid:
        sid = await uow.skin_inventory.get_using(uid, aid)
        if sid:
            sname, sdesc, img = await uow.skins.get_info(sid)
            sdesc = sdesc.strip()
            desc = sdesc or desc
        new = await uow.inventories.get_stats(uid, aid) > 0
    else:
        new = False

    return AwardInfo(
        aid=aid,
        name=aname,
        description=desc,
        level=level,
        image=Path(img),
        sid=sid,
        skin_name=sname,
        new=new,
        notation="",
    )


async def generate_random_info():
    """
    生成一个合成失败时的乱码小哥信息
    """

    rlen = get_random().randint(2, 4)
    rlen2 = get_random().randint(30, 90)
    rchar = lambda: chr(get_random().randint(0x4E00, 0x9FFF))

    return AwardInfo(
        aid=-1,
        name="".join((rchar() for _ in range(rlen))),
        description="".join((rchar() for _ in range(rlen2))),
        image=imageToBytes(await make_strange()),
        level=level_repo.levels[0],
        sid=None,
        skin_name=None,
        new=False,
        notation="",
    )


async def uow_use_award(uow: UnitOfWork, uid: int, aid: int, count: int):
    """在大规模重构之前提供的临时方法，用来让用户使用小哥，如果数量不够则报错

    Args:
        uow (UnitOfWork): 工作单元
        uid (int): 用户 ID
        aid (int): 小哥 ID
        count (int): 数量
    """
    sto, _ = await uow.inventories.give(uid, aid, -count)
    if sto < 0:
        raise LackException(
            (await uow_get_award_info(uow, aid)).name, count, sto + count
        )


async def get_award_info_deprecated(session: AsyncSession, uid: int, aid: int):
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

    info = AwardInfoDeprecated(
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


@deprecated("该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息")
async def set_inventory(
    session: AsyncSession, uid: int, aid: int, storage: int, used: int
):
    """设置玩家的小哥的库存信息

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 ID
        aid (int): 小哥 ID
        storage (int): 库存有多少小哥
        used (int): 用过多少小哥
    """

    await InventoryRepository(session).set_inventory(uid, aid, storage, used)


@deprecated("该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息")
async def get_inventory(session: AsyncSession, uid: int, aid: int) -> tuple[int, int]:
    """获得小哥物品栏的原始信息

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户的 ID
        aid (int): 小哥的 ID

    Returns:
        tuple[int, int]: 两项分别是库存中有多少小哥，目前用掉了多少小哥
    """

    return await InventoryRepository(session).get_inventory(uid, aid)


@deprecated("该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息")
async def get_storage(session: AsyncSession, uid: int, aid: int):
    """返回用户库存里有多少小哥

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 uid
        aid (int): 小哥 id

    Returns:
        int: 库存小哥的数量
    """
    return await InventoryRepository(session).get_storage(uid, aid)


@deprecated("该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息")
async def get_statistics(session: AsyncSession, uid: int, aid: int):
    """获得迄今为止一共抓到了多少小哥

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户在数据库中的 ID
        aid (int): 小哥在数据库中的 ID

    Returns:
        int: 累计的小哥数量
    """
    return await InventoryRepository(session).get_stats(uid, aid)


@deprecated("该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息")
async def give_award(
    session: AsyncSession, uid: int, aid: int, count: int, report_lack: bool = True
):
    """增减一个用户的小哥库存

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户 ID
        aid (int): 小哥 ID
        count (int): 增减数量。如果值小于 0，会记录使用的量。
        report_lack (bool): 是否在小哥数量不够时抛出异常，默认为 True
    """
    sto, _ = await InventoryRepository(session).give(uid, aid, count)
    if sto < 0 and count < 0 and report_lack:
        raise LackException(
            (await get_award_info_deprecated(session, uid, aid)).awardName,
            -count,
            sto - count,
        )


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
