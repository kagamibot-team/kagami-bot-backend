from src.base.command_events import MessageContext, GroupContext
from src.common.config import get_config


def isAdmin(ctx: MessageContext) -> bool:
    if isinstance(ctx, GroupContext):
        if ctx.event.group_id in get_config().admin_groups:
            return True

    if ctx.sender_id == get_config().admin_id:
        return True

    return False
