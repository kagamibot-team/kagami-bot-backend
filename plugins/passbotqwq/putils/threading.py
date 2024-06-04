import asyncio

from typing import Callable, TypeVar, ParamSpec


T = TypeVar("T")
P = ParamSpec("P")


def make_async(func: Callable[P, T]):
    async def _func(*args: P.args, **kwargs: P.kwargs):
        loop = asyncio.get_event_loop()
    
        def _roughly_run():
            return func(*args, **kwargs)

        return await loop.run_in_executor(None, _roughly_run)

    return _func
