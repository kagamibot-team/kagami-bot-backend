from src.base.command_events import GroupContext, MessageContext
from src.common.config import get_config


def is_admin(ctx: MessageContext) -> bool:
    if isinstance(ctx, GroupContext):
        if ctx.event.group_id in get_config().admin_groups:
            return True

    if ctx.sender_id == get_config().admin_id:
        return True

    return False
