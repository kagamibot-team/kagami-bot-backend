from ..base.command_events import ConsoleContext, GroupContext, Context
from ..common.config import config


def isAdmin(ctx: Context) -> bool:
    if isinstance(ctx, ConsoleContext):
        return True

    if isinstance(ctx, GroupContext):
        if ctx.event.group_id in config.admin_groups:
            return True

    if ctx.getSenderId() == config.admin_id:
        return True

    return False
