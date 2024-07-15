"""
和项目有关的一些枚举类的需求
"""

from typing import Generic, TypeVar

T = TypeVar("T")


class PriorityList(Generic[T]):
    """
    优先级列表，在事件系统中使用，是一个带有优先级的序列。
    这个序列可以按照需要的优先级插入元素。
    """

    ls: list[tuple[int, T]]

    def __init__(self):
        self.ls = []

    def add(self, item: T, priority: int=0):
        """添加元素

        Args:
            priority (int): 优先级
            item (T): 需要新加入的元素
        """

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
