import random

from src.common.fast_import import *
from .catch_time import *


async def pickAwards(session: AsyncSession, uid: int, count: int) -> Picks:
    """
    在内存中进行一次抓小哥，结果先不会保存到数据库中。
    调用该函数前，请**一定要**先验证 `count` 是否在合适范围内。

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户在数据库中的 ID
        count (int): 抓小哥的次数

    Returns:
        Picks: 抓小哥结果的记录
    """

    picks = Picks(awards={}, money=0)
    assert count >= 0

    # 初始化一些会重复用的量
    query = select(Level.data_id, Level.weight, Level.price).filter(Level.weight > 0)
    levels = (await session.execute(query)).tuples().all()

    # 开始抓小哥
    for _ in range(count):
        if len(levels) == 0:
            logger.error("数据库中没有等级")
            break

        level = random.choices(levels, [l[1] for l in levels])[0]

        # 这里是在数据库中随机抽取该等级的小哥的操作
        # 据说有速度更快的写法……
        query = (
            select(Award.data_id)
            .filter(Award.level_id == level[0])
            .order_by(func.random())
            .limit(1)
        )

        award = (await session.execute(query)).scalar_one_or_none()

        if award is None:
            logger.warning(f"没有小哥在 ID 为 {level} 的等级中")
            continue

        if award in picks.awards.keys():
            picks.awards[award].delta += 1
        else:
            picks.awards[award] = Pick(await get_statistics(session, uid, award), 1)
        
        picks.money += level[2]

    return picks
