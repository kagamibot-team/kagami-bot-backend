from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar
from arclet.alconna import Alconna


T = TypeVar('T')


class AlconnaCommand(ABC, Generic[T]):
    """
    Alconna命令类
    """

    rule: Alconna

    def __init__(self, rule: Alconna):
        self.rule = rule

    async def handle(self, event: T):
        ...
