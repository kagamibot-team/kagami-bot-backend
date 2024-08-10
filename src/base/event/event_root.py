"""
和根事件监听器有关的模块
"""

import time
from typing import Any
from nonebot import on_notice, on_type  # type: ignore
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    LifecycleMetaEvent,
    NoticeEvent,
    NotifyEvent,
    PrivateMessageEvent,
)

from src.base.command_events import GroupContext, PrivateContext
from src.base.event.event_manager import EventManager
from src.base.onebot.onebot_events import (
    GroupMessageEmojiLike,
    GroupPoke,
    GroupPokeContext,
    GroupStickEmojiContext,
    OnebotStartedContext,
)
from src.base.onebot.onebot_tools import record_last_context
from src.common.config import config


MESSAGE_LAST_TIME: dict[int, float] = {}


def check_last_time(sender: int | None) -> bool:
    """用于消息限制频率

    Args:
        sender (int): 消息的发送者的 ID

    Returns:
        bool: 是否达到了频率限制
    """

    sender = sender or 0

    last_time = MESSAGE_LAST_TIME.get(sender, 0)
    now = time.time()
    MESSAGE_LAST_TIME[sender] = now

    return now - last_time < 1


def activate_root(event_root: EventManager):
    """激活事件监听器，让事件监听器挂载到 Nonebot 原生的事件上

    Args:
        event_root (EventManager): 事件管理器
    """

    groupMessageHandler = on_type(GroupMessageEvent)
    privateMessageHandler = on_type(PrivateMessageEvent)

    notice_group_msg_emoji_like_handler = on_notice()
    onebot_startup_hander = on_type(LifecycleMetaEvent)

    @groupMessageHandler.handle()
    async def _(bot: Bot, event: GroupMessageEvent):
        if config.enable_white_list and event.group_id not in config.white_list_groups:
            return
        if check_last_time(event.sender.user_id):
            return
        record_last_context(event.user_id, event.group_id)

        await event_root.throw(GroupContext(event, bot))

    @privateMessageHandler.handle()
    async def _(bot: Bot, event: PrivateMessageEvent):
        if check_last_time(event.sender.user_id):
            return
        record_last_context(event.user_id, None)
        await event_root.throw(PrivateContext(event, bot))

    @notice_group_msg_emoji_like_handler.handle()
    async def _(bot: Bot, event: NoticeEvent):
        if event.notice_type == "group_msg_emoji_like":
            await event_root.throw(
                GroupStickEmojiContext(GroupMessageEmojiLike(**event.model_dump()), bot)
            )
        if event.notice_type == "notify" and isinstance(event, NotifyEvent):
            if event.sub_type == "poke":
                await event_root.throw(
                    GroupPokeContext(
                        GroupPoke(
                            time=event.time,
                            self_id=event.self_id,
                            group_id=event.group_id,
                            user_id=event.user_id,
                            target_id=getattr(event, "target_id"),
                        ),
                        bot,
                    )
                )

    @onebot_startup_hander.handle()
    async def _(bot: Bot, event: LifecycleMetaEvent):
        if event.sub_type == "connect":
            await event_root.throw(OnebotStartedContext(bot))


async def throw_event(event: Any):
    await root.throw(event)


async def emit_event(event: Any):
    await root.emit(event)


root = EventManager()


__all__ = ["root", "activate_root"]
