"""
该模块正在考虑废弃，请考虑使用 InventoryRespository 管理库存信息
"""

import uuid

from loguru import logger

import src
import src.ui
import src.ui.types
import src.ui.types.common
from src.base.exceptions import LackException
from src.base.res import KagamiResourceManagers
from src.base.res.resource import IResource
from src.common.download import download
from src.common.rd import get_random
from src.common.threading import make_async
from src.core.unit_of_work import UnitOfWork
from src.models.level import level_repo
from src.models.models import *
from src.ui.base.strange import make_strange
from src.ui.base.tools import image_to_bytes


async def get_award_info(
    uow: UnitOfWork, aid: int, uid: int | None = None, sid: int | None = None
):
    if uid is not None and sid is not None:
        raise ValueError("请不要同时启用 uid 和 sid 两个参数")
    data = await uow.awards.get_info(aid)

    if uid:
        sid = await uow.skin_inventory.get_using(uid, aid)
    if sid:
        sinfo = await uow.skins.get_info_v2(sid)
        data = sinfo.link(data)
    return data


async def generate_random_info(uow: UnitOfWork) -> src.ui.types.common.AwardInfo:
    """
    生成一个合成失败时的乱码小哥信息
    """

    # 获取所有的小哥和皮肤图片
    sources: list[IResource] = []

    aids: set[int] = set()
    for pid in range(0, await uow.settings.get_pack_count() + 1):
        aids.update(await uow.pack.get_main_aids_of_pack(pid))
    aids.update(await uow.awards.get_aids(lid=0))
    for aid in aids:
        sources.append(KagamiResourceManagers.xiaoge(f"aid_{aid}.png"))

    sids: set[int] = await uow.skins.all_sid()
    for sid in sids:
        sources.append(KagamiResourceManagers.xiaoge(f"sid_{sid}.png"))

    # 生成乱码
    rlen = get_random().randint(2, 4)
    rlen2 = get_random().randint(30, 90)
    rchar = lambda: chr(get_random().randint(0x4E00, 0x9FFF))
    img = await make_async(make_strange)(sources)
    img_name = f"tmp_{uuid.uuid4().hex}.png"

    aif = src.ui.types.common.AwardInfo(
        name="".join((rchar() for _ in range(rlen))),
        description="".join((rchar() for _ in range(rlen2))),
        level=level_repo.get_data_by_id(0),
        aid=-1,
        sorting=0,
    )
    aif._img_resource = KagamiResourceManagers.tmp.put(img_name, image_to_bytes(img))
    return aif


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
    data = await download(url)
    logger.debug(f"将图片资源保存至：aid_{aid}.png")
    KagamiResourceManagers.xiaoge.put(f"aid_{aid}.png", data)
