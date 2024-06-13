from typing import Any, Awaitable, Callable, Generic, TypeVar

from nonebot import logger


T = TypeVar("T")
TV = TypeVar("TV", contravariant=True)


Listener = Callable[[TV], Awaitable[Any]]


def _isinstance(obj: Any, typ: type):
    try:
        return isinstance(obj, typ)
    except TypeError:
        return False


class PriorityList(Generic[T]):
    ls: list[tuple[int, T]]

    def __init__(self):
        self.ls = []

    def add(self, priority: int, item: T):
        i = 0
        while i < len(self.ls):
            if self.ls[i][0] > priority:
                break
            i += 1
        self.ls.insert(i, (priority, item))
    
    def __iter__(self):
        return (item for _, item in self.ls)

    def __len__(self):
        return len(self.ls)

    def __getitem__(self, index: int):
        return self.ls[index][1]


class EventManager(dict[type[Any], PriorityList[Listener[Any]]]):
    def listen(self, evtType: type[TV], *, priority: int = 0):
        def decorator(func: Listener[TV]):
            if evtType not in self.keys():
                self[evtType] = PriorityList()
            self[evtType].add(priority, func)

        return decorator

    def listens(self, *evtTypes: type[TV], priority: int = 0):
        def decorator(func: Listener[TV]):
            for evtType in evtTypes:
                self.listen(evtType, priority=priority)(func)

        return decorator

    async def emit(self, evt: Any):
        for key in self.keys():
            if _isinstance(evt, key):
                try:
                    for l in self[key]:
                        await l(evt)
                except StopIteration:
                    pass
    
    def merge(self, other: "EventManager"):
        for key in other.keys():
            if key not in self.keys():
                self[key] = other[key]
            else:
                for l in other[key].ls:
                    self[key].add(l[0], l[1])
