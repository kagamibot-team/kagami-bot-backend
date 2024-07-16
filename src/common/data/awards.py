"""
该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息
"""

import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.exceptions import LackException
from src.common.data.skins import get_using_skin
from src.common.dataclasses.award_info import AwardInfoDeprecated
from src.common.download import download, writeData
from src.common.draw.strange import make_strange
from src.common.draw.tools import imageToBytes
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork
from src.models.models import *
from src.models.statics import level_repo
from src.repositories.award_repository import AwardRepository
from src.repositories.inventory_repository import InventoryRepository
from src.views.award import AwardInfo


def award_info_from_uow(
    uow: UnitOfWork,
    aid: int,
    name: str,
    description: str,
    level_id: int,
    image: str,
    is_special_get_only: bool,
    sorting: int,
):
    """
    用来获取一个小哥的基础信息

    Args:
        uow (UnitOfWork): 工作单元
        aid (int): 小哥 ID
        name (str): 小哥名称
        description (str): 小哥描述
        level_id (int): 小哥等级
        image (str): 小哥图片
        is_special_get_only (bool): 是否只能通过特殊方式获得
        sorting (int): 排序
    """
    return AwardInfo(
        aid=aid,
        name=name,
        description=description,
        level=uow.levels.get_by_id(level_id),
        image=Path(image),
        sid=None,
        skin_name=None,
        new=False,
        notation="",
    )


async def get_award_info(
    uow: UnitOfWork, aid: int, uid: int | None = None, sid: int | None = None
):
    """用来获取一个小哥的基础信息

    Args:
        uow (UnitOfWork): 工作单元
        aid (int): 小哥 ID
        uid (int | None, optional): 用户 ID，可留空，用来获取皮肤的信息. Defaults to None.
    """
    if uid is not None and sid is not None:
        raise ValueError("请不要同时启用 uid 和 sid 两个参数")

    aname, desc, lid, img = await uow.awards.get_info(aid)
    level = uow.levels.get_by_id(lid)
    sname = None
    new = False

    if uid:
        sid = await uow.skin_inventory.get_using(uid, aid)
        new = await uow.inventories.get_stats(uid, aid) > 0
    if sid:
        sname, sdesc, img = await uow.skins.get_info(sid)
        sdesc = sdesc.strip()
        desc = sdesc or desc

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


async def get_a_list_of_award_info(
    uow: UnitOfWork, uid: int | None, aids: list[int]
) -> list[AwardInfo]:
    """用来获取多个小哥的基础信息

    Args:
        uow (UnitOfWork): 工作单元
        aids (list[int]): 小哥 ID 列表
    """
    basics = await uow.awards.get_list_of_award_info(aids)
    basics = [award_info_from_uow(uow, *info) for info in basics]

    if uid is None:
        return basics

    using = await uow.skin_inventory.get_using_list(uid)
    for info in basics:
        if info.aid in using:
            sid = using[info.aid]
            info.sid = sid
            sname, sdesc, img = await uow.skins.get_info(sid)
            info.skin_name = sname
            info.description = sdesc.strip() or info.description
            info.image = Path(img)

        info.new = await uow.inventories.get_stats(uid, info.aid) > 0

    return basics


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


async def use_award(uow: UnitOfWork, uid: int, aid: int, count: int):
    """用来让用户使用小哥，如果数量不够则报错

    Args:
        uow (UnitOfWork): 工作单元
        uid (int): 用户 ID
        aid (int): 小哥 ID
        count (int): 数量
    """
    sto, _ = await uow.inventories.give(uid, aid, -count)
    if sto < 0:
        raise LackException((await get_award_info(uow, aid)).name, count, sto + count)


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


async def get_aid_by_name(session: AsyncSession, name: str):
    return await AwardRepository(session).get_aid(name)


async def download_award_image(aid: int, url: str):
    uIndex: int = 0

    def _path():
        return Path("./data/awards") / f"{aid}_{uIndex}.png"

    while _path().exists():
        uIndex += 1

    await writeData(await download(url), _path())

    return _path().as_posix()
