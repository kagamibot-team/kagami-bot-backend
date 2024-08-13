from ..base.command_events import MessageContext, GroupContext
from ..common.config import config


def isAdmin(ctx: MessageContext) -> bool:
    if isinstance(ctx, GroupContext):
        if ctx.event.group_id in config.admin_groups:
            return True

    if ctx.sender_id == config.admin_id:
        return True

    return False
