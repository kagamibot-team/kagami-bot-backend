from typing import Awaitable, Callable

from pydantic import BaseModel

from src.base.command_events import MessageContext
from src.base.localstorage import LocalStorage
from src.common.config import get_config


class GlobalFlags(BaseModel):
    activity_hua_out: bool = False


def global_flags():
    return LocalStorage(get_config().global_data_path).context("flags", GlobalFlags)


def require_hua_out(func: Callable[[MessageContext], Awaitable[None]]):
    async def inner(ctx: MessageContext):
        with global_flags() as data:
            if not data.activity_hua_out:
                return
        return await func(ctx)

    return inner
