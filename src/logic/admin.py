from ..events.context import ConsoleMessageContext, OnebotGroupMessageContext, OnebotPrivateMessageContext, PublicContext
from ..config import config


def isAdmin(ctx: PublicContext) -> bool:
    if isinstance(ctx, ConsoleMessageContext):
        return True

    if isinstance(ctx, OnebotGroupMessageContext):
        if ctx.event.group_id in config.admin_groups:
            return True
        if ctx.event.user_id == config.admin_id:
            return True

    if isinstance(ctx, OnebotPrivateMessageContext):
        if ctx.event.user_id == config.admin_id:
            return True

    return False
