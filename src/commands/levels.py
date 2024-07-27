from nonebot_plugin_alconna import UniMessage
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchRegex,
    requireAdmin,
)
from src.common.lang.zh import la
from src.core.unit_of_work import get_unit_of_work
from src.models.models import Award
from src.models.level import level_repo


@listenOnebot()
@requireAdmin()
@matchRegex("^:: ?(所有|全部) ?(等级|级别) ?$")
async def _(ctx: OnebotContext, _):
    async with get_unit_of_work() as uow:
        query = select(
            Award.level_id,
            func.count(Award.data_id),
        ).group_by(Award.level_id)
        counts = dict((await uow.session.execute(query)).tuples().all())
    levels = [
        (level.lid, level.display_name, level.weight, level.color, level.awarding)
        for level in level_repo.sorted
    ]

    weight_sum = sum((l[2] for l in levels))

    message = UniMessage("===== 所有等级 =====")

    for lid, name, weight, color_code, price in levels:
        if weight_sum > 0:
            prob = f"权重{weight} 概率{round(weight / weight_sum * 100, 2)}%"
        else:
            prob = f"权重{weight}"

        message += f"\n- {name}[{color_code}] {prob} 奖励 {price}{la.unit.money} 共有 {counts[lid]} 小哥"

    await ctx.send(message)
