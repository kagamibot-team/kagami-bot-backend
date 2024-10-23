from abc import ABC, abstractmethod


class ITextFilter(ABC):
    @abstractmethod
    def match(self, text: str) -> bool: ...


class WithPrefixFilter(ITextFilter):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def match(self, text: str) -> bool:
        return text.startswith(self.prefix)


class WithSuffixFilter(ITextFilter):
    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def match(self, text: str) -> bool:
        return text.endswith(self.suffix)
