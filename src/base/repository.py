"""
# `repository` Module Documentation
The `repository` module provides a base class for repository implementations
in a SQLAlchemy-based application. This base class, BaseRepository,
encapsulates common CRUD operations, promoting code reuse and consistency
across different repositories.

---

中国语版本：

# `repository` 模块文档
`repository` 模块为基于 SQLAlchemy 的应用程序提供了一个用于实现仓库的基类。
这个基类 BaseRepository 封装了常见的 CRUD 操作，促进了不同仓库之间代码的重用
和一致性。

---

该模块的思路源自 ChatGPT。
"""

from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base

T = TypeVar("T", bound="Base")


class BaseRepository(Generic[T]):
    """
    基础的数据库仓库，用于管理一个特定的数据库表。
    """

    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def get_all(self) -> list[T]:
        return list((await self.session.execute(select(self.model))).scalars().all())

    async def add(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete(self, obj: T) -> None:
        await self.session.delete(obj)
        await self.session.flush()

    async def delete_by_id(self, id: int) -> None:
        obj = await self.get_by_id(id)
        if obj:
            await self.delete(obj)

    async def update(self, obj: T) -> T:
        await self.session.flush()
        return obj


__all__ = ["BaseRepository"]
