from loguru import logger
from sqlalchemy import func, select

from src.common.dataclasses import Pick, Picks
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork
from src.models.level import level_repo
from src.models.models import Award


async def pickAwards(uow: UnitOfWork, uid: int, count: int) -> Picks:
    """
    在内存中进行一次抓小哥，结果先不会保存到数据库中。
    调用该函数前，请**一定要**先验证 `count` 是否在合适范围内。

    Args:
        uow (UnitOfWork): 工作单元
        uid (int): 用户在数据库中的 ID
        count (int): 抓小哥的次数

    Returns:
        Picks: 抓小哥结果的记录
    """

    picks = Picks(awards={}, money=0, uid=uid)
    assert count >= 0

    # 开始抓小哥
    for _ in range(count):
        if await uow.users.do_have_flag(uid, "是"):
            await uow.users.remove_flag(uid, "是")
            shi = await uow.awards.get_aid("是小哥")
            if shi is None:
                pass
            elif shi in picks.awards.keys():
                picks.awards[shi].delta += 1
                picks.money += uow.levels.get_by_id(1).awarding
                continue
            else:
                picks.awards[shi] = Pick(
                    beforeStats=await uow.inventories.get_stats(uid, shi),
                    delta=1,
                    level=0,
                )
                picks.money += uow.levels.get_by_id(1).awarding
                continue

        level = get_random().choices(
            level_repo.sorted, [l.weight for l in level_repo.sorted]
        )[0]

        # 这里是在数据库中随机抽取该等级的小哥的操作
        # 据说有速度更快的写法……
        query = (
            select(Award.data_id)
            .filter(
                Award.level_id == level.lid,
                Award.is_special_get_only.is_not(True),
            )
            .order_by(func.random())
            .limit(1)
        )

        aid = (await uow.session.execute(query)).scalar_one_or_none()

        if aid is None:
            logger.warning(f"没有小哥在 ID 为 {level} 的等级中")
            continue

        if aid in picks.awards.keys():
            picks.awards[aid].delta += 1
        else:
            picks.awards[aid] = Pick(
                beforeStats=await uow.inventories.get_stats(uid, aid),
                delta=1,
                level=level.lid,
            )

        picks.money += level.awarding

    return picks
