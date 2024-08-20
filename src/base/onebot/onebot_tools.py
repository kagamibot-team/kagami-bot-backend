import asyncio

import nonebot
from loguru import logger

from src.base.onebot.onebot_api import (
    get_group_list,
    get_group_member_list,
    get_stranger_name,
    send_group_msg,
    send_private_msg,
)
from src.base.onebot.onebot_basic import MessageLike, OnebotBotProtocol
from src.common.config import config

LAST_CONTEXT_RECORDER: dict[int, int] = {}


def record_last_context(qqid: int, group_id: int | None = None):
    if group_id is None:
        LAST_CONTEXT_RECORDER.pop(qqid, None)
    else:
        LAST_CONTEXT_RECORDER[qqid] = group_id


async def broadcast(
    bot: OnebotBotProtocol, message: MessageLike, require_admin: bool = False
):
    group_list = await get_group_list(bot)

    for group in group_list:
        if config.enable_white_list and group.group_id not in config.white_list_groups:
            continue
        if require_admin and group not in config.admin_groups:
            continue

        await send_group_msg(bot, group.group_id, message)
        await asyncio.sleep(0.2)


async def tell(qqid: int, message: MessageLike, bot: OnebotBotProtocol | None = None):
    if bot is None:
        bot = nonebot.get_bot()

    if qqid not in LAST_CONTEXT_RECORDER:
        await send_private_msg(bot, qqid, message)
    else:
        await send_group_msg(bot, LAST_CONTEXT_RECORDER[qqid], message)


CACHED_NAME_GROUP: dict[int, dict[int, str]] = {}


async def update_cached_name(bot: OnebotBotProtocol, group_id: int):
    ls = await get_group_member_list(bot, group_id)
    CACHED_NAME_GROUP[group_id] = {}
    for d in ls:
        if len(d["card"]) > 0:
            CACHED_NAME_GROUP[group_id][int(d["user_id"])] = d["card"]
    logger.info(f"群 {group_id} 群成员信息刷新了一次")


async def get_name_cached(
    group_id: int | None, qqid: int, bot: OnebotBotProtocol | None = None
) -> str:
    if bot is None:
        bot = nonebot.get_bot()
    name: str = await get_stranger_name(bot, qqid)
    if group_id is not None:
        if group_id not in CACHED_NAME_GROUP:
            await update_cached_name(bot, group_id)
        if group_id in CACHED_NAME_GROUP:
            if qqid not in CACHED_NAME_GROUP[group_id]:
                await update_cached_name(bot, group_id)
            if qqid in CACHED_NAME_GROUP[group_id]:
                name = CACHED_NAME_GROUP[group_id][qqid]
    if len(name) == 0:
        return str(qqid)
    return name
