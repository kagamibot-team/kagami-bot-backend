"""
该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息
"""

import uuid
from pathlib import Path

import src
import src.ui
import src.ui.types
import src.ui.types.common
from src.base.exceptions import LackException
from src.common.download import download, writeData
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork
from src.models.level import level_repo
from src.models.models import *
from src.ui.base.strange import make_strange
from src.common.threading import make_async


async def get_award_info(
    uow: UnitOfWork, aid: int, uid: int | None = None, sid: int | None = None
):
    if uid is not None and sid is not None:
        raise ValueError("请不要同时启用 uid 和 sid 两个参数")
    data = await uow.awards.get_info(aid)
    if uid:
        sid = await uow.skin_inventory.get_using(uid, aid)
    if sid:
        await uow.skins.link(sid, data)
    return data


async def generate_random_info():
    """
    生成一个合成失败时的乱码小哥信息
    """

    rlen = get_random().randint(2, 4)
    rlen2 = get_random().randint(30, 90)
    rchar = lambda: chr(get_random().randint(0x4E00, 0x9FFF))
    img = await make_async(make_strange)()
    img_name = f"tmp_{uuid.uuid4().hex}.png"
    img.save(Path("./data/temp/") / img_name)

    return src.ui.types.common.AwardInfo(
        name="".join((rchar() for _ in range(rlen))),
        description="".join((rchar() for _ in range(rlen2))),
        image_name=img_name,
        image_type="temp",
        level=level_repo.get_data_by_id(0),
        color=level_repo.get_data_by_id(0).color,
        aid=-1,
        sorting=0,
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


async def download_award_image(aid: int, url: str):
    uIndex: int = 0

    def _path():
        return Path("./data/awards") / f"{aid}_{uIndex}.png"

    while _path().exists():
        uIndex += 1

    await writeData(await download(url), _path())

    return _path().as_posix()
