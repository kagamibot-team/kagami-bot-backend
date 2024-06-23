"""
## 关于 API

详见 https://napneko.github.io/zh-CN/develop/api
以及 https://napneko.github.io/zh-CN/develop/extends_api

若在测试环境中：
详见 https://llonebot.github.io/zh-CN/develop/api
以及 https://llonebot.github.io/zh-CN/develop/extends_api

请保证调用的 API 在 NapNeko 中有相应实现
"""

from src.base.onebot_basic import handle_input_message, OnebotBotProtocol, MessageLike
from src.common.qq_emoji_enum import QQEmoji


async def send_group_msg(
    bot: OnebotBotProtocol,
    group_id: int,
    message: MessageLike,
):
    return await bot.call_api(
        "send_group_msg", group_id=group_id, message=handle_input_message(message)
    )


async def send_private_msg(
    bot: OnebotBotProtocol,
    user_id: int,
    message: MessageLike,
):
    return await bot.call_api(
        "send_private_msg", user_id=user_id, message=handle_input_message(message)
    )


async def delete_msg(
    bot: OnebotBotProtocol,
    message_id: int,
):
    await bot.call_api("delete_msg", message_id=message_id)


async def set_msg_emoji_like(
    bot: OnebotBotProtocol, message_id: int, emoji_id: int | str | QQEmoji
):
    if isinstance(emoji_id, QQEmoji):
        emoji_id = emoji_id.value

    await bot.call_api(
        "set_msg_emoji_like",
        message_id=message_id,
        emoji_id=str(emoji_id),
    )
