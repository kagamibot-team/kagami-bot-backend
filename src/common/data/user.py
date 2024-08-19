from src.base.command_events import MessageContext
from src.core.unit_of_work import UnitOfWork
from src.ui.types.common import UserData


async def get_user_data(ctx: MessageContext, uow: UnitOfWork):
    return UserData(
        uid=await uow.users.get_uid(ctx.sender_id),
        qqid=str(ctx.sender_id),
        name=await ctx.get_sender_name(),
    )
