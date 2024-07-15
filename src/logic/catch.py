from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.dataclasses import Picks, Pick
from src.common.data.users import get_user_flags, set_user_flags
from sqlalchemy import func, select
from src.models.models import Award
from src.common.data.awards import get_statistics
from src.common.rd import get_random
from src.models.statics import level_repo


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

    picks = Picks(awards={}, money=0, uid=uid)
    assert count >= 0

    # 开始抓小哥
    for _ in range(count):
        flags = await get_user_flags(session, uid)
        if "是" in flags:
            flags.remove("是")
            await set_user_flags(session, uid, flags)
            have_shi = select(Award.data_id).filter(Award.name == "是小哥")
            shi = (await session.execute(have_shi)).scalar_one_or_none()

            if shi is None:
                pass
            elif shi in picks.awards.keys():
                picks.awards[shi].delta += 1
                continue
            else:
                picks.awards[shi] = Pick(
                    beforeStats=await get_statistics(session, uid, shi),
                    delta=1,
                    level=0,
                )
                continue

        level = get_random().choices(level_repo.sorted, [l.weight for l in level_repo.sorted])[0]

        # 这里是在数据库中随机抽取该等级的小哥的操作
        # 据说有速度更快的写法……
        query = (
            select(Award.data_id)
            .filter(Award.level_id == level.lid, Award.is_special_get_only == False) # pylint: disable=singleton-comparison
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
            picks.awards[award] = Pick(
                beforeStats=await get_statistics(session, uid, award),
                delta=1,
                level=level.lid,
            )

        picks.money += level.awarding

    return picks
