import asyncio
import time
from typing import Any, Callable, Coroutine, TypeVar

from loguru import logger

from src.base.exceptions import KagamiStopIteration
from utils.collections import PriorityList

T = TypeVar("T")
TV_contra = TypeVar("TV_contra", contravariant=True)


Listener = Callable[[TV_contra], Coroutine[Any, Any, Any]]


def _isinstance(obj: Any, typ: type):
    try:
        return isinstance(obj, typ)
    except TypeError:
        return False


class EventManager(dict[type[Any], PriorityList[Listener[Any]]]):
    """
    用于整个 Bot 的事件系统

    使用方法:

    ```python
    event = EventManager()

    @event.listen(EventType)
    async def event_handler(event: EventType):
        ... # do something
    ```

    此时这个函数就会监听所有类型为 `EventType` 的 `event` 事件，当有事件触发时，会执行 `event_handler` 函数。

    当需要触发事件时，可以使用 `event.emit(event)` 触发事件，事件系统会根据事件类型和优先级执行事件处理函数。

    如果希望监听多个事件，可以使用 `event.listens(*eventTypes)` 方法，其中 `*eventTypes` 表示要监听的事件类型。

    如果想要触发事件而不等待处理函数执行完成，可以使用 `event.throw(event)` 方法。
    """

    def listen(self, evtType: type[TV_contra], *, priority: int = 0):
        """
        监听事件，`evtType` 表示事件类型，`priority` 表示优先级，优先级高的函数会先执行。
        """

        def decorator(func: Listener[TV_contra]):
            if evtType not in self.keys():
                self[evtType] = PriorityList()
            self[evtType].add(priority=priority, item=func)

        return decorator

    def listens(self, *evtTypes: type[TV_contra], priority: int = 0):
        """
        监听多个事件，`priority` 表示优先级，优先级高的函数会先执行。
        """

        def decorator(func: Listener[TV_contra]):
            for evtType in evtTypes:
                self.listen(evtType, priority=priority)(func)

        return decorator

    async def emit(self, evt: Any):
        """
        触发事件，并等待事件处理函数执行完成。
        """

        begin = time.time()
        for key, vals in self.items():
            if _isinstance(evt, key):
                for l in vals:
                    try:
                        await l(evt)
                    except KagamiStopIteration:
                        break
        logger.debug(f"Event {repr(evt)} emitted in {time.time() - begin}s")

    async def throw(self, evt: Any):
        """
        触发事件，并立即返回。
        """

        tasks: set[asyncio.Task[Any]] = set()

        for key, vals in self.items():
            if _isinstance(evt, key):
                for l in vals:
                    task = asyncio.create_task(l(evt))
                    tasks.add(task)
                    task.add_done_callback(tasks.discard)


__all__ = ["EventManager", "Listener"]
