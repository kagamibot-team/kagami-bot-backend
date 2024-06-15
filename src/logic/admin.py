from ..events.context import ConsoleContext, OnebotGroupContext, OnebotPrivateContext, PublicContext
from ..config import config


def isAdmin(ctx: PublicContext) -> bool:
    if isinstance(ctx, ConsoleContext):
        return True

    if isinstance(ctx, OnebotGroupContext):
        if ctx.event.group_id in config.admin_groups:
            return True
        if ctx.event.user_id == config.admin_id:
            return True

    if isinstance(ctx, OnebotPrivateContext):
        if ctx.event.user_id == config.admin_id:
            return True

    return False
