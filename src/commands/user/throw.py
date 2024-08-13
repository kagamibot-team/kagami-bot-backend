from src.base.command_events import MessageContext
from src.common.command_decorators import listen_message


@listen_message()
async def _(ctx: MessageContext):
    ...
