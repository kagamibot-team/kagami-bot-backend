from typing import Generic, TypeVar


T = TypeVar("T")


class PriorityList(Generic[T]):
    ls: list[tuple[int, T]]

    def __init__(self):
        self.ls = []

    def add(self, priority: int, item: T):
        i = 0
        while i < len(self.ls):
            if self.ls[i][0] < priority:
                break
            i += 1
        self.ls.insert(i, (priority, item))

    def __iter__(self):
        return (item for _, item in self.ls)

    def __len__(self):
        return len(self.ls)

    def __getitem__(self, index: int):
        return self.ls[index][1]
    
    def __str__(self) -> str:
        return f"PriorityList({self.ls})"

    def __repr__(self) -> str:
        return f"PriorityList({self.ls})"
