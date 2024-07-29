"""
该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息
"""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.exceptions import LackException
from src.common.download import download, writeData
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork
from src.models.models import *
from src.models.level import level_repo
from src.repositories.inventory_repository import InventoryRepository
from src.ui.base.strange import make_strange
from src.ui.base.tools import image_to_bytes
from src.ui.views.award import AwardInfo, StorageDisplay
from utils.threading import make_async


def award_info_from_uow(
    uow: UnitOfWork,
    aid: int,
    name: str,
    description: str,
    level_id: int,
    image: str,
    is_special_get_only: bool,
    sorting: int,
) -> tuple[int, AwardInfo]:
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
    return aid, AwardInfo(
        aid=aid,
        name=name,
        description=description,
        level=uow.levels.get_by_id(level_id),
        image=Path(image),
        sid=None,
        skin_name=None,
        sorting=sorting,
        is_special_get_only=is_special_get_only,
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

    if uid:
        sid = await uow.skin_inventory.get_using(uid, aid)
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
    )


async def get_a_list_of_award_storage(
    uow: UnitOfWork, uid: int | None, aids: list[int], show_notation2: bool = True
) -> list[StorageDisplay | None]:
    """用来获取多个小哥的基础信息

    Args:
        uow (UnitOfWork): 工作单元
        aids (list[StorageDisplay | None]): 小哥 ID 列表
    """
    _basics = await uow.awards.get_list_of_award_info(aids)
    basics: list[StorageDisplay | None] = list(
        (
            StorageDisplay(
                storage=0,
                stats=0,
                do_show_notation2=False,
                do_show_notation1=False,
                info=award_info_from_uow(uow, *info)[1],
            )
            for info in _basics
        )
    )
    if uid is None:
        return basics

    using = await uow.skin_inventory.get_using_list(uid)
    for i, info in enumerate(basics):
        if info is None:
            continue

        aid = info.info.aid
        info.do_show_notation1 = True
        info.do_show_notation2 = show_notation2

        sto, use = await uow.inventories.get_inventory(uid, aid)
        if sto + use == 0:
            basics[i] = None
            continue

        info.storage = sto
        info.stats = sto + use
        if aid in using:
            sid = using[aid]
            info.info.sid = sid
            sname, sdesc, img = await uow.skins.get_info(sid)
            info.info.skin_name = sname
            info.info.description = sdesc.strip() or info.info.description
            info.info.image = Path(img)

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
        image=image_to_bytes(await make_async(make_strange)()),
        level=level_repo.levels[0],
        sid=None,
        skin_name=None,
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


async def download_award_image(aid: int, url: str):
    uIndex: int = 0

    def _path():
        return Path("./data/awards") / f"{aid}_{uIndex}.png"

    while _path().exists():
        uIndex += 1

    await writeData(await download(url), _path())

    return _path().as_posix()
