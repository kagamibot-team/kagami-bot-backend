from typing import Callable


A_SIMPLE_RULE = Callable[[str], bool]

def isFloat() -> A_SIMPLE_RULE:
    def inner(x: str):
        try:
            float(x)
            return True
        except:
            pass
        return False

    return inner


def combine(*rules: Callable[[str], bool]):
    def inner(x: str):
        for rule in rules:
            if not rule(x):
                return False

        return True

    return inner

def not_negative():
    def inner(x: str):
        return float(x) >= 0

    return combine(isFloat(), inner)