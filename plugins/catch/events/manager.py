import inspect
from typing import Any, Awaitable, Callable, Protocol, Type, TypeVar, cast


T = TypeVar("T", contravariant=True)


Listener = Callable[[T], Awaitable[Any]]


def _isinstance(obj: Any, typ: type):
    try:
        return isinstance(obj, typ)
    except TypeError:
        return False


class EventManager(dict[type[Any], list[Listener[Any]]]):
    def listen(self, evtType: type[T]):
        def decorator(func: Listener[T]):
            if evtType not in self.keys():
                self[evtType] = []
            self[evtType].append(func)

        return decorator

    def listens(self, *evtTypes: type[T]):
        def decorator(func: Listener[T]):
            for evtType in evtTypes:
                self.listen(evtType)(func)

        return decorator

    async def emit(self, evt: Any):
        for key in self.keys():
            if _isinstance(evt, key):
                for l in self[key]:
                    await l(evt)
