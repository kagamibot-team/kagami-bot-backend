from typing import Any

from arclet.alconna import Alconna, Arparma

from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import listenOnebot, matchAlconna
from src.core.unit_of_work import get_unit_of_work
from src.services.achievement import Achievement, get_achievement_service


def get_single_achievement_msg(achievement: Achievement, achieved: bool) -> str:
    _achieved = "[已达成] " if achieved else ""
    msg = f"{_achieved}{achievement.name}\n"
    msg += f"    {achievement.description}"

    return msg


@listenOnebot()
@matchAlconna(Alconna("re:(我的|my)(成就|cj)"))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = await get_achievement_service(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        display: list[str] = []
        for a in service.achievements:
            if await a.check_can_display(uow, uid):
                display.append(get_single_achievement_msg(a, await a.have_got(uow, uid)))

    await ctx.reply("\n\n".join(display))
