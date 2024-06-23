from nonebot import logger, on_notice, on_type  # type: ignore
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    PrivateMessageEvent,
    NoticeEvent,
)
from nonebot.adapters.console import Bot as ConsoleBot
from nonebot.adapters.console import MessageEvent as ConsoleMessageEvent

from src.base.event_manager import EventManager
from src.base.onebot_events import GroupMessageEmojiLike, GroupStickEmojiContext
from .command_events import (
    ConsoleContext,
    GroupContext,
    PrivateContext,
)

from src.common.config import config


def activateRoot(root: EventManager):
    consoleHandler = on_type(ConsoleMessageEvent)
    groupMessageHandler = on_type(GroupMessageEvent)
    privateMessageHandler = on_type(PrivateMessageEvent)

    notice_group_msg_emoji_like_handler = on_notice()

    @consoleHandler.handle()
    async def _(bot: ConsoleBot, event: ConsoleMessageEvent):
        await root.throw(ConsoleContext(event, bot))

    @groupMessageHandler.handle()
    async def _(bot: Bot, event: GroupMessageEvent):
        if config.enable_white_list and event.group_id not in config.white_list_groups:
            return

        await root.throw(GroupContext(event, bot))

    @privateMessageHandler.handle()
    async def _(bot: Bot, event: PrivateMessageEvent):
        await root.throw(PrivateContext(event, bot))

    @notice_group_msg_emoji_like_handler.handle()
    async def _(bot: Bot, event: NoticeEvent):
        if event.notice_type == "group_msg_emoji_like":
            await root.throw(
                GroupStickEmojiContext(GroupMessageEmojiLike(**event.model_dump()), bot)
            )


root = EventManager()


__all__ = ["root", "activateRoot"]
