"""
## 关于 API

详见 https://napneko.github.io/zh-CN/develop/api
以及 https://napneko.github.io/zh-CN/develop/extends_api

若在测试环境中：
详见 https://llonebot.github.io/zh-CN/develop/api
以及 https://llonebot.github.io/zh-CN/develop/extends_api

请保证调用的 API 在 NapNeko 中有相应实现
"""

import asyncio
import datetime
from io import BytesIO
from typing import Any

import PIL
import PIL.Image
import requests
from nonebot.adapters.onebot.v11.exception import ActionFailed
from pydantic import BaseModel

from src.base.onebot.onebot_basic import (
    MessageLike,
    OnebotBotProtocol,
    handle_input_message,
)
from src.base.onebot.onebot_enum import QQEmoji, QQStatus


async def send_group_msg(
    bot: OnebotBotProtocol,
    group_id: int,
    message: MessageLike,
):
    result = await bot.call_api(
        "send_group_msg", group_id=group_id, message=handle_input_message(message)
    )
    return result


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
    bot: OnebotBotProtocol, message_id: str, emoji_id: int | str | QQEmoji
):
    if isinstance(emoji_id, QQEmoji):
        emoji_id = emoji_id.value

    await bot.call_api(
        "set_msg_emoji_like",
        message_id=message_id,
        emoji_id=str(emoji_id),
    )


class GroupInfo(BaseModel):
    group_id: int
    group_name: str
    member_count: int
    max_member_count: int


async def get_group_list(bot: OnebotBotProtocol) -> list[GroupInfo]:
    res: list[dict] = await bot.call_api("get_group_list")
    return [GroupInfo(**v) for v in res]


async def set_qq_status(
    bot: OnebotBotProtocol,
    status: QQStatus | tuple[int, int] = QQStatus.在线,
    batteryStatus: int = 0,
):
    if isinstance(status, QQStatus):
        status = status.value

    await bot.call_api(
        "set_online_status",
        status=status[0],
        extStatus=status[1],
        batteryStatus=batteryStatus,
    )


async def get_group_member_info(bot: OnebotBotProtocol, group_id: int, user_id: int):
    return await bot.call_api(
        "get_group_member_info",
        group_id=group_id,
        user_id=user_id,
        no_cache=True,
    )


async def get_stranger_name(bot: OnebotBotProtocol, qqid: int | str) -> str:
    try:
        info: dict[str, Any] = await bot.call_api("get_stranger_info", user_id=qqid)
        name: str = info.get("nick", "")
        return name
    except ActionFailed:
        # Fallback 方案
        return str(qqid)


async def get_group_member_list(
    bot: OnebotBotProtocol, group_id: int
) -> list[dict[str, Any]]:
    try:
        data: list[dict[str, Any]] = await bot.call_api(
            "get_group_member_list", group_id=group_id
        )
        return data
    except ActionFailed:
        return []


async def get_name(
    bot: OnebotBotProtocol, qqid: int | str, group_id: int | None
) -> str:
    try:
        info: dict[str, Any] = await bot.call_api("get_stranger_info", user_id=qqid)
        name: str = info.get("nick", "")

        if group_id is not None:
            info = await bot.call_api(
                "get_group_member_info",
                group_id=group_id,
                user_id=qqid,
                no_cache=True,
            )
            name: str = info.get("nickname", "")
            name = info.get("card", "") or name

        return name
    except ActionFailed:
        # 拿不到名称，因为这时候那个人应该就退群了，例如，盐酸。。。。
        return str(qqid)


async def is_group_operator(bot: OnebotBotProtocol, group_id: int, user_id: int):
    info = await get_group_member_info(bot, group_id, user_id)
    return info["role"] == "owner" or info["role"] == "admin"


async def set_group_ban(
    bot: OnebotBotProtocol,
    group_id: int,
    user_id: int,
    duration: int | datetime.timedelta,
):
    """设置禁言

    Args:
        bot (OnebotBotProtocol): Bot
        group_id (int): 群 ID
        user_id (int): 用户名
        duration (int): 禁言时长，单位为秒
    """

    if isinstance(duration, datetime.timedelta):
        duration = duration.seconds

    await bot.call_api(
        "set_group_ban",
        group_id=group_id,
        user_id=user_id,
        duration=duration,
    )


async def get_avatar_image(user_id: int):
    """获取头像

    Args:
        user_id (int): QQ 号

    Returns:
        PIL.Image.Image: PIL 的图像对象
    """
    loop = asyncio.get_event_loop()
    req = await loop.run_in_executor(
        None,
        requests.get,
        f"http://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640&img_type=jpg",
    )
    return PIL.Image.open(BytesIO(req.content), "r")
