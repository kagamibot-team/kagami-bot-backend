from ..common.classes.command_events import ConsoleContext, GroupContext, PrivateContext, PublicContext
from ..common.config import config


def isAdmin(ctx: PublicContext) -> bool:
    if isinstance(ctx, ConsoleContext):
        return True

    if isinstance(ctx, GroupContext):
        if ctx.event.group_id in config.admin_groups:
            return True
        if ctx.event.user_id == config.admin_id:
            return True

    if isinstance(ctx, PrivateContext):
        if ctx.event.user_id == config.admin_id:
            return True

    return False
