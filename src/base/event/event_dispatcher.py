import asyncio
import time
from typing import Any, Callable, Coroutine, TypeVar

from loguru import logger

from src.base.exceptions import KagamiStopIteration
from src.common.collections import PriorityList

T = TypeVar("T")
TV_contra = TypeVar("TV_contra", contravariant=True)


Listener = Callable[[TV_contra], Coroutine[Any, Any, Any]]


def _isinstance(obj: Any, typ: type):
    try:
        return isinstance(obj, typ)
    except TypeError:
        return False


class EventDispatcher:
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

    listeners: dict[type[Any], PriorityList[Listener[Any]]]
    linked: set["EventDispatcher"]

    def __init__(self) -> None:
        self.listeners = {}
        self.linked = set()
        self.parents = set()

    def listen(self, evtType: type[TV_contra], *, priority: int = 0):
        """
        监听事件，`evtType` 表示事件类型，`priority` 表示优先级，优先级高的函数会先执行。
        """

        def decorator(func: Listener[TV_contra]):
            if evtType not in self.listeners.keys():
                self.listeners[evtType] = PriorityList()
            self.listeners[evtType].add(priority=priority, item=func)

        return decorator

    def listens(self, *evtTypes: type[TV_contra], priority: int = 0):
        """
        监听多个事件，`priority` 表示优先级，优先级高的函数会先执行。
        """

        def decorator(func: Listener[TV_contra]):
            for evtType in evtTypes:
                self.listen(evtType, priority=priority)(func)

        return decorator

    def link(self, sub_dispatcher: "EventDispatcher"):
        self.linked.add(sub_dispatcher)
        sub_dispatcher.linked.add(self)

    async def emit(
        self, evt: Any, proceeded_dispatcher: set["EventDispatcher"] | None = None
    ):
        """
        触发事件，并等待事件处理函数执行完成。
        """

        proceeded_dispatcher = proceeded_dispatcher or set()
        if self in proceeded_dispatcher:
            return
        begin = time.time()
        for key, vals in self.listeners.items():
            if _isinstance(evt, key):
                for l in vals:
                    try:
                        await l(evt)
                    except KagamiStopIteration:
                        break
        for node in self.linked:
            await node.emit(evt, proceeded_dispatcher | {self})
        logger.debug(f"Event {repr(evt)} emitted in {time.time() - begin}s")

    async def throw(
        self, evt: Any, proceeded_dispatcher: set["EventDispatcher"] | None = None
    ):
        """
        触发事件，并立即返回。
        """

        proceeded_dispatcher = proceeded_dispatcher or set()
        if self in proceeded_dispatcher:
            return
        tasks: set[asyncio.Task[Any]] = set()
        for key, vals in self.listeners.items():
            if _isinstance(evt, key):
                for l in vals:
                    task = asyncio.create_task(l(evt))
                    tasks.add(task)
                    task.add_done_callback(tasks.discard)
        for node in self.linked:
            await node.throw(evt, proceeded_dispatcher | {self})


__all__ = ["EventDispatcher", "Listener"]
