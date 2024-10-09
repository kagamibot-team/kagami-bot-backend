from arclet.alconna import Alconna

from src.base.command_events import MessageContext
from src.common.command_deco import listen_message, match_alconna
from src.core.unit_of_work import get_unit_of_work
from src.services.achievements.base import Achievement, get_achievement_service
from src.ui.types.achievement import AchievementDisplay


def get_single_achievement_msg(display: AchievementDisplay) -> str:
    achieved = display.achieved
    achievement = display.meta
    _achieved = "[ √ 已达成] " if achieved else "[ × 未达成] "
    msg = f"{_achieved}{achievement.name}\n"
    msg += f"    {achievement.description}"

    return msg


@listen_message()
@match_alconna(Alconna("re:(我的|my)(成就|cj)"))
async def _(ctx: MessageContext, _):
    async with get_unit_of_work(ctx.sender_id) as uow:
        service = get_achievement_service()
        uid = await uow.users.get_uid(ctx.sender_id)
        display: list[str] = []
        for a in service.achievements:
            disp = await AchievementDisplay.get(uow, a, uid)
            if not disp.should_display:
                continue
            display.append(get_single_achievement_msg(disp))

    await ctx.send(
        f" 成就列表\n 当前用户：{await ctx.sender_name}\n\n" + "\n\n".join(display)
    )
