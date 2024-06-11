import inspect
from typing import Any, Awaitable, Protocol, Type, cast


class Listener(Protocol):
    def __call__(self, arg: Any) -> Awaitable[Any]:
        ...


def _isinstance(obj: Any, typ: type):
    try:
        return isinstance(obj, typ)
    except TypeError:
        return False


class EventManager:
    listeners: dict[Type[Any], list[Listener]]

    def __init__(self) -> None:
        self.listeners = {}

    def listen(self, listener: Listener):
        sig = inspect.signature(listener)
        param_type = sig.parameters['arg'].annotation

        if param_type not in self.listeners.keys():
            self.listeners[param_type] = [listener]
        else:
            self.listeners[param_type].append(listener)
    
    async def emit(self, evt: Any):
        for key in self.listeners.keys():
            if _isinstance(evt, key):
                for l in self.listeners[key]:
                    await l(evt)
    
    def __add__(self, one: "EventManager"):
        new = EventManager()
        for key in self.listeners.keys():
            new.listeners[key] = list(self.listeners[key])
        
        for key in one.listeners.keys():
            if key in new.listeners.keys():
                new.listeners[key] += one.listeners[key]
            else:
                new.listeners[key] = one.listeners[key]
        
        return new
