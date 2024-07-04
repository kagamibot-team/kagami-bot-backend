from pydantic import BaseModel

from src.base.command_events import OnebotBotProtocol


class GroupEmoji(BaseModel):
    emoji_id: str
    count: int


class GroupMessageEmojiLike(BaseModel):
    time: int
    self_id: int
    group_id: int
    user_id: int
    message_id: int
    likes: list[GroupEmoji]


class GroupStickEmojiContext:
    event: GroupMessageEmojiLike
    bot: OnebotBotProtocol

    def __init__(self, event: GroupMessageEmojiLike, bot: OnebotBotProtocol) -> None:
        self.event = event
        self.bot = bot


class OnebotStartedContext:
    bot: OnebotBotProtocol

    def __init__(self, bot: OnebotBotProtocol) -> None:
        self.bot = bot


__all__ = [
    "GroupEmoji",
    "GroupMessageEmojiLike",
    "GroupStickEmojiContext",
    "OnebotStartedContext",
]
