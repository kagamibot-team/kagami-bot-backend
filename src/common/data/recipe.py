"""
和小哥合成有关的各种东西
"""

from dataclasses import dataclass
import itertools
import math
import random
import statistics

from nonebot import logger
from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Award, AwardTagRelation, Level, Recipe, Tag


async def _get_lid(session: AsyncSession, a: int):
    return (
        (
            await session.execute(
                select(Award.level_id, Level.weight)
                .join(Level, Award.level_id == Level.data_id)
                .filter(Award.data_id == a)
            )
        )
        .tuples()
        .one()
    )


async def generate_random_result(
    session: AsyncSession, a1: int, a2: int, a3: int
) -> tuple[int, float]:
    """生成一个随机的合成配方

    Args:
        session (AsyncSession): 数据库会话
        a1 (int): 第一个小哥 aid
        a2 (int): 第二个小哥 aid
        a3 (int): 第三个小哥 aid

    Returns:
        tuple[int, float]: 合成出来的小哥 aid 和合成概率
    """

    # 获得所有的 Level 的信息
    # 拿到的数据应该是
    #   - 1: 65.0
    #   - 2: 24.5
    #   - 3: 8.0
    #   - 4: 2.0
    #   - 5: 0.5
    query = (
        select(Level.data_id, Level.weight)
        .filter(Level.weight > 0)
        .join(Award, Award.level_id == Level.data_id)
        .group_by(Level.data_id)
        .order_by(-Level.weight)
    )
    levels = (await session.execute(query)).tuples().all()
    levels_qr = {lid: i for i, (lid, _) in enumerate(levels)}

    # 获得三个小哥的等级 ID
    lid1, w1 = await _get_lid(session, a1)
    lid2, w2 = await _get_lid(session, a2)
    lid3, w3 = await _get_lid(session, a3)

    # 如果含有零星小哥，那么合成产物一定是零星小哥（lid=7），我们对于「成功」产物，就随机生成一个值返回吧。
    if lid1 == 7 or lid2 == 7 or lid3 == 7:
        # 小哥的 data_id 是 5
        return 5, 0.0

    a0 = max(lid1, lid2, lid3)
    b0 = 7 - ((lid1**2 + lid2**2 + lid3**2)/3)**(1/2) - a0/10 # b0越小越赚，先减去综合实力，再减去最高等级增益

    # 抽取一个等级
    r = Recipe.get_random_object(a1, a2, a3).betavariate(a0, b0)
    lid: int | None = None
    lid = math.ceil(r*5)

    logger.info(f"{lid1}+{lid2}+{lid3}={lid} ({r}, [{a0}, {b0}])")


    rms = ((lid1**2 + lid2**2 + lid3**2)/3) ** 0.5 # 三个等级的平方平均数
    fvi = (rms/5)**(1/10) # 变换为配方珍贵指数(0.851~1)

    poss = 1 - lid/8 # 基础概率，由产物等级决定 (0.875, 0.75, 0.625, 0.5, 0.375)
    poss = poss ** (1 + (lid - max(lid1, lid2, lid3))/5) # 综合概率，由产物等级与材料最高级之差影响，升级则降低概率
    poss = poss * fvi # 最终概率，由配方珍贵程度影响，影响程度较小

    logger.info(f"{1 - lid/8}^(1 + {lid - max(lid1, lid2, lid3)}/5)*{fvi} = {poss}")

    query = select(Award.data_id).filter(Award.level_id == lid, Award.is_special_get_only == False)
    aids = (await session.execute(query)).scalars().all()
    aid = Recipe.get_random_object(a1, a2, a3).choice(aids)

    return aid, poss


async def get_merge_result(
    session: AsyncSession, a1: int, a2: int, a3: int
) -> tuple[int, float]:
    """获得一个合成配方合成的结果的 data_id，在计算时会进行排序使该合成为无序配方

    Args:
        session (AsyncSession): 数据库会话
        a1 (int): 第一个小哥 aid
        a2 (int): 第二个小哥 aid
        a3 (int): 第三个小哥 aid

    Returns:
        tuple[int, float]: 合成出来的小哥 aid 和合成概率
    """

    a1, a2, a3 = sorted((a1, a2, a3))

    query = select(Recipe.result, Recipe.possibility).filter(
        Recipe.award1 == a1, Recipe.award2 == a2, Recipe.award3 == a3
    )
    result = (await session.execute(query)).tuples().one_or_none()

    if result is not None:
        return result

    result, possibility = await generate_random_result(session, a1, a2, a3)
    await session.execute(
        insert(Recipe).values(
            award1=a1, award2=a2, award3=a3, result=result, possibility=possibility
        )
    )
    return result, possibility


async def clear_all_recipe(session: AsyncSession):
    await session.execute(delete(Recipe))


async def try_merge(
    session: AsyncSession, uid: int, a1: int, a2: int, a3: int
) -> tuple[int, bool]:
    """进行一次小哥合成，并返回合成的结果

    Args:
        session (AsyncSession): 数据库会话
        uid (int): 用户的 uid，在未来可能会有跟幸运值有关的判断
        a1 (int): 第一个小哥 aid
        a2 (int): 第二个小哥 aid
        a3 (int): 第三个小哥 aid

    Returns:
        int: 合成出来的小哥的 aid
    """

    result, possibility = await get_merge_result(session, a1, a2, a3)

    if random.random() <= possibility:
        return result, True

    if random.random() <= 0.8:
        # 粑粑小哥
        return 89, False

    if random.random() <= 0.5:
        # 对此时有特殊情况，是乱码小哥
        return -1, False

    query = (
        select(Award.data_id)
        .filter(Award.level_id == 7)
        .order_by(func.random())
        .limit(1)
    )
    result = (await session.execute(query)).scalar_one()

    return result, False
