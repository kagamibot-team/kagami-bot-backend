# 尼玛的，有些库没办法导入，我只能复制粘贴


# Comparison protocols

from typing import Any, Protocol, TypeAlias, TypeVar


_T_contra = TypeVar("_T_contra", contravariant=True)


class SupportsDunderLT(Protocol[_T_contra]):
    def __lt__(self, other: _T_contra, /) -> bool: ...

class SupportsDunderGT(Protocol[_T_contra]):
    def __gt__(self, other: _T_contra, /) -> bool: ...

class SupportsDunderLE(Protocol[_T_contra]):
    def __le__(self, other: _T_contra, /) -> bool: ...

class SupportsDunderGE(Protocol[_T_contra]):
    def __ge__(self, other: _T_contra, /) -> bool: ...


SupportsRichComparison: TypeAlias = SupportsDunderLT[Any] | SupportsDunderGT[Any]
