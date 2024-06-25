import asyncio
from typing import Any, Awaitable, Callable

from src.base.event_root import root


class IntervalEvent:
    id: int
    interval: float

    def __init__(self, interval: float) -> None:
        self.interval = interval
        self.id = IntervalEvent.itv_id
        self.cleared = False

        IntervalEvent.itv_id += 1
        IntervalEvent.events.append(self)

    @staticmethod
    def clear(id: int):
        oe = [e for e in IntervalEvent.events if e.id == id]
        for e in oe:
            e.cleared = True
            IntervalEvent.events.remove(e)

    itv_id: int = 0
    events: list["IntervalEvent"] = []


def addInterval(
    interval: float, func: Callable[[], Awaitable[Any]], skip_first: bool = True
):
    """创建一个定时任务

    Args:
        interval (float): 周期，单位秒
        func (Callable[[], Awaitable[Any]]): 一个异步函数的引用，这个异步函数不输入任何信息
        skip_first (bool, optional): 是否跳过第一次（即 0 秒时）运行函数. Defaults to True.

    Returns:
        int: 定时任务的 ID
    """
    itv = IntervalEvent(interval)

    async def inner(_itv: IntervalEvent):
        if _itv.id == itv.id:
            await func()
            if _itv.cleared:
                itv.cleared = True

    root.listen(IntervalEvent)(inner)

    async def _cycle():
        if not skip_first:
            await root.throw(itv)

        while not itv.cleared:
            await asyncio.sleep(interval)
            await root.throw(itv)

    _cycle_backup: set[asyncio.Task[None]] = set()
    eventloop = asyncio.get_event_loop()

    task = eventloop.create_task(_cycle())
    task.add_done_callback(_cycle_backup.discard)

    return itv.id


def addTimeout(timeout: float, func: Callable[[], Awaitable[Any]]):
    """创建一个不阻塞的延时任务

    Args:
        timeout (float): 延时的事件
        func (Callable[[], Awaitable[Any]]): 一个异步函数的名字，这个异步函数应该不输入任何量
    """

    async def _task():
        await asyncio.sleep(timeout)
        await func()

    _task_backup: set[asyncio.Task[None]] = set()
    eventloop = asyncio.get_event_loop()

    task = eventloop.create_task(_task())
    task.add_done_callback(_task_backup.discard)


def clearInterval(id: int):
    """清空定时任务

    Args:
        id (int): 定时任务的 ID
    """
    IntervalEvent.clear(id)


__all__ = ["clearInterval", "addInterval", "addTimeout"]
