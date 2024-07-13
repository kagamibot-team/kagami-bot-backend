from ..base.command_events import GroupContext, OnebotContext
from ..common.config import config


def isAdmin(ctx: OnebotContext) -> bool:
    if isinstance(ctx, GroupContext):
        if ctx.event.group_id in config.admin_groups:
            return True

    if ctx.sender_id == config.admin_id:
        return True

    return False
