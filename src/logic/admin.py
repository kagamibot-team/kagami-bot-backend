from ..base.command_events import GroupContext, GroupContext
from ..common.config import config


def isAdmin(ctx: GroupContext) -> bool:
    if isinstance(ctx, GroupContext):
        if ctx.event.group_id in config.admin_groups:
            return True

    if ctx.sender_id == config.admin_id:
        return True

    return False
