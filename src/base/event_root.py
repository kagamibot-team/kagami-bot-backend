"""
和根事件监听器有关的模块
"""

from nonebot import on_notice, on_type  # type: ignore
from nonebot.adapters.console import Bot as ConsoleBot
from nonebot.adapters.console import MessageEvent as ConsoleMessageEvent
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    LifecycleMetaEvent,
    NoticeEvent,
    PrivateMessageEvent,
)

from src.base.command_events import ConsoleContext, GroupContext, PrivateContext
from src.base.event_manager import EventManager
from src.base.onebot_events import (
    GroupMessageEmojiLike,
    GroupStickEmojiContext,
    OnebotStartedContext,
)
from src.common.config import config


def activate_root(event_root: EventManager):
    """激活事件监听器，让事件监听器挂载到 Nonebot 原生的事件上

    Args:
        event_root (EventManager): 事件管理器
    """

    consoleHandler = on_type(ConsoleMessageEvent)
    groupMessageHandler = on_type(GroupMessageEvent)
    privateMessageHandler = on_type(PrivateMessageEvent)

    notice_group_msg_emoji_like_handler = on_notice()
    onebot_startup_hander = on_type(LifecycleMetaEvent)

    @consoleHandler.handle()
    async def _(bot: ConsoleBot, event: ConsoleMessageEvent):
        await event_root.throw(ConsoleContext(event, bot))

    @groupMessageHandler.handle()
    async def _(bot: Bot, event: GroupMessageEvent):
        if config.enable_white_list and event.group_id not in config.white_list_groups:
            return

        await event_root.throw(GroupContext(event, bot))

    @privateMessageHandler.handle()
    async def _(bot: Bot, event: PrivateMessageEvent):
        await event_root.throw(PrivateContext(event, bot))

    @notice_group_msg_emoji_like_handler.handle()
    async def _(bot: Bot, event: NoticeEvent):
        if event.notice_type == "group_msg_emoji_like":
            await event_root.throw(
                GroupStickEmojiContext(GroupMessageEmojiLike(**event.model_dump()), bot)
            )

    @onebot_startup_hander.handle()
    async def _(bot: Bot, event: LifecycleMetaEvent):
        if event.sub_type == "connect":
            await event_root.throw(OnebotStartedContext(bot))


root = EventManager()


__all__ = ["root", "activate_root"]
