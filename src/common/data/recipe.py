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

    _id1 = -1 if lid1 not in levels_qr.keys() else levels_qr[lid1]
    _id2 = -1 if lid2 not in levels_qr.keys() else levels_qr[lid2]
    _id3 = -1 if lid3 not in levels_qr.keys() else levels_qr[lid3]

    # 计算各等级的聚合频率
    # 在当前的数据库中，聚合频率为：
    #   - 一星 0.650
    #   - 二星 0.895
    #   - 三星 0.975
    #   - 四星 0.995
    #   - 五星 1.000
    weight_sum = sum([r[1] for r in levels])
    acc_possibility = list(
        itertools.accumulate([r[1] / weight_sum for r in levels])
    ) + [0]
    fall1 = acc_possibility[_id1]
    fall2 = acc_possibility[_id2]
    fall3 = acc_possibility[_id3]

    # 成功率偏执，也就是里面最高星的那个的聚合频率的相反数加上其等级本身的
    # 权重的结果，也同时作为整个合成的期望。其实就是抽到高于或等于该等级小
    # 哥的概率。
    # 在当前数据库中的值：
    #   - 一星 1.000
    #   - 二星 0.350
    #   - 三星 0.105
    #   - 四星 0.025
    #   - 五星 0.005
    bias = 1 - max(fall1, fall2, fall3) + min(w1, w2, w3) / weight_sum

    # 将成功因子相乘，并进行变换，得到珍贵程度。只要出现了零星小哥，它的值
    # 就会是 0。
    # 珍贵程度是三个成功因子的几何平均值，例如这些值：
    #   - 111: 0.650
    #   - 211: 0.723
    #   - 221: 0.804
    #   - 311: 0.744
    #   - 411: 0.749
    #   - 422: 0.927
    #   - 511: 0.750（例如，把五星扔回炉子里再造）
    succ = fall1 * fall2 * fall3
    succ: float = succ ** (1 / 3)

    # 珍贵程度乘以成功率偏执，再进行变换，就是成功率了，结果示例：
    #   - 111: 0.898
    #   - 211: 0.709
    #   - 311: 0.529
    #   - 411: 0.370
    #   - 511: 0.247
    poss = succ * bias
    poss = poss**0.25

    # 如果 poss 为 0，那么合成产物一定是零星小哥，我们对于「成功」产物，就
    # 随机生成一个值返回吧。
    if poss == 0:
        # 小哥的 data_id 是 5
        return 5, 0.0

    # 在成功合成时，其期望需要经过修正。因为我们希望最终的期望是刚好等于
    # bias 的，所以在这里，我们需要修正等下进行贝塔分布的计算时，期望的值。
    # 但是，其实这里存在一个问题，就是当我们的 bias 本身就很高的时候，通过
    # 修正期望已经做不到将全局期望修正回留级的值了，没办法，这个期望会大于
    # 1，所以我们用一个 arctan 函数进行压缩。

    # 这时候，111 合成成功时，期望是 0.267
    # 211 合成成功时，期望是 0.839
    # 311 合成成功时，期望是 0.871（这时候已经需要玩家去拿高等级一点的去砸了）
    a0 = (1 - bias * 0.9) / poss
    a0 = math.atan(a0 * 8) / math.pi * 2
    b0 = 1 - a0

    # 根据标准差确定 a0 和 b0 的系数，越分散，结果的分散程度越要大，那么系
    # 数就要小。
    scalar = statistics.pvariance([fall1, fall2, fall3])
    scalar = 1 / (1 + scalar * 0.2) * 20

    # 最后，抽取一个等级
    r = Recipe.get_random_object(a1, a2, a3).betavariate(a0 * scalar, b0 * scalar)
    lid: int | None = None

    logger.info(r)
    logger.info(poss)

    for i, p in enumerate(acc_possibility):
        # 若当前的汇聚概率大于抽取到的值，则离开
        if p > r:
            lid = levels[i][0]
            break

    if lid is None:
        # 极其罕见事件之 r == 1
        lid = levels[-1][0]

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

    if random.random() <= 0.75:
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
