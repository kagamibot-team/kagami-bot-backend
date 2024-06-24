from src.base.onebot_api import get_group_list, send_group_msg
from src.base.onebot_basic import MessageLike, OnebotBotProtocol
from src.common.config import config


async def broadcast(bot: OnebotBotProtocol, message: MessageLike):
    group_list = await get_group_list(bot)

    for group in group_list:
        if config.enable_white_list and group.group_id not in config.white_list_groups:
            continue

        await send_group_msg(bot, group.group_id, message)
