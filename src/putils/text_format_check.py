from typing import Callable

import re


A_SIMPLE_RULE = Callable[[str], bool]


def checkFormat(
    text: str, rules: list[A_SIMPLE_RULE] = [], weakRules: list[A_SIMPLE_RULE] = []
) -> bool:
    args = text.split(" ")

    if len(rules) > len(args) or len(args) > len(rules) + len(weakRules):
        return False

    for i, v in enumerate(args):
        if i >= len(rules):
            if not weakRules[i - len(rules)](v):
                return False
            continue

        if not rules[i](v):
            return False

    return True


def literal(text: str) -> A_SIMPLE_RULE:
    def inner(x: str):
        return str(x) == text

    return inner


def regex(rule: str | re.Pattern[str]) -> A_SIMPLE_RULE:
    def inner(x: str):
        return re.match(rule, x) != None

    return inner


def isDigit() -> A_SIMPLE_RULE:
    def inner(x: str):
        return x.isdecimal()

    return inner


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


def ok():
    def inner(x: str):
        return True

    return inner


def not_negative():
    def inner(x: str):
        return float(x) >= 0

    return combine(isFloat(), inner)


def matchCommand(text: str, rule: A_SIMPLE_RULE):
    return rule(text.split(" ")[0])
