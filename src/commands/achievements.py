from typing import Any

from arclet.alconna import Alconna, Arparma

from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import listenOnebot, matchAlconna
from src.core.unit_of_work import get_unit_of_work
from src.services.achievement import Achievement, get_achievement_service


@listenOnebot()
@matchAlconna(Alconna("re:(我的|my)(成就|cj)"))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = await get_achievement_service(uow)
        uid = await uow.users.get_uid(ctx.sender_id)
        display: list[tuple[Achievement, bool]] = []
        for a in service.achievements:
            if await a.check_can_display(uow, uid):
                display.append((a, await a.have_got(uow, uid)))
    await ctx.reply(str(display))
