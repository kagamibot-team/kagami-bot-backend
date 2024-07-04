from src.imports import *


@listenPublic()
@requireAdmin()
@matchRegex("^:: ?(所有|全部) ?(等级|级别) ?$")
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, _):
    query = (
        select(
            Level.name,
            Level.weight,
            Level.color_code,
            Level.price,
            func.count(Award.data_id),
        )
        .join(Award, Award.level_id == Level.data_id)
        .group_by(Level.data_id)
        .order_by(-Level.sorting_priority, Level.weight)
    )
    levels = (await session.execute(query)).tuples().all()

    weight_sum = sum((l[1] for l in levels))

    message = UniMessage("===== 所有等级 =====")

    for name, weight, color_code, price, award_count in levels:
        if weight_sum > 0:
            prob = f"权重{weight} 概率{round(weight / weight_sum * 100, 2)}%"
        else:
            prob = f"权重{weight}"

        message += f"\n- {name}[{color_code}] {prob} 奖励 {price}{la.unit.money} 共有 {award_count} 小哥"

    await ctx.send(message)
