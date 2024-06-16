from typing import Any, Literal
from nepattern import BasePattern, MatchMode
from nonebot_plugin_alconna import Text


class GreedyTextMatcher(BasePattern[str, Text | str, Literal[MatchMode.KEEP]]):
    def __init__(self):
        super().__init__(mode=MatchMode.KEEP, alias="Text*", origin=[Text, str])

    def match(self, input_: Text | str) -> str:
        if isinstance(input_, Text):
            input_ = input_.text
        return input_
    
    def __calc_eq__(self, other: Any):  # pragma: no cover
        return other.__class__ is GreedyTextMatcher
    

__all__ = ("GreedyTextMatcher",)
