from typing import Awaitable, Callable

from src.base.command_events import MessageContext
from src.base.localstorage import LocalStorage
from src.common.config import get_config
from src.ui.types.common import GlobalFlags


def global_flags():
    return LocalStorage(get_config().global_data_path).context("flags", GlobalFlags)


def require_hua_out(func: Callable[[MessageContext], Awaitable[None]]):
    async def inner(ctx: MessageContext):
        async with global_flags() as data:
            if not data.activity_hua_out:
                return
        return await func(ctx)

    return inner
