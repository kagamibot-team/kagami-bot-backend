from typing import Any

from nonebot_plugin_alconna import UniMessage

from src.base.event.event_root import root
from src.base.onebot.onebot_tools import tell
from src.common.dataclasses.game_events import UserDataUpdatedEvent
from src.core.unit_of_work import get_unit_of_work
from src.services.achievements.base import (
    Achievement,
    AnnounceRule,
    get_achievement_service,
)
from src.ui.types.common import UserData


async def render_achievement_message(
    user: UserData,
    achievements: list[Achievement],
) -> UniMessage[Any]:
    return UniMessage.at(user_id=user.qqid).text(
        " 恭喜你，刚才获得了这些成就：\n"
        + "".join(["\n- " + str(a) for a in achievements])
    )


@root.listen(UserDataUpdatedEvent)
async def _(event: UserDataUpdatedEvent):
    async with get_unit_of_work(event.uid) as uow:
        service = get_achievement_service()
        results = await service.update(uow, event)

    if len(results) > 0:
        message = await render_achievement_message(
            event.user_data,
            [r for r in results if r.announce_rule != AnnounceRule.no_announcement],
        )
        await tell(int(event.user_data.qqid), message)
