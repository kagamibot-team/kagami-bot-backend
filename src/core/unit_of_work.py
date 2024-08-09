"""
# Unit of Work Pattern
Implement the Unit of Work pattern to manage transactions and coordinate
changes across multiple repositories. This pattern helps ensure that all
database operations within a transaction are committed or rolled back together.

---

中国语版本：

# 工作单元模式
实现工作单元模式来管理事务并协调多个仓库之间的变更。该模式有助于确保事务内的所
有数据库操作要么全部提交，要么全部回滚。

---

该模块的思路源自 ChatGPT。
"""

import asyncio
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.lock_manager import get_lock
from src.models.level import level_repo
from src.repositories.skin_inventory_repository import SkinInventoryRepository
from src.repositories.up_pool_repository import UpPoolRepository
from src.repositories.user_repository import (
    MoneyRepository,
    UserFlagRepository,
    UserPackRepository,
)

from ..base.db import DatabaseManager
from ..repositories import (
    AwardRepository,
    InventoryRepository,
    RecipeRepository,
    SettingRepository,
    SkinRepository,
    UserRepository,
)


class UnitOfWork:
    """
    一个工作单元。这个工作单元能够提供相关数据库操作仓库的上下文。
    因为要保证线程安全性，所以引入了一个参数，用于方便管理锁
    """

    db_manager: DatabaseManager
    _session: AsyncSession | None
    lock: asyncio.Lock | None

    def __init__(
        self, db_manager: DatabaseManager, lock: asyncio.Lock | None = None
    ) -> None:
        self.db_manager = db_manager
        self._session = None
        self.lock = lock

    @property
    def session(self) -> AsyncSession:
        """获得当前工作单元的数据库会话。

        Raises:
            RuntimeError: 如果当前的工作单元还没有被初始化，则抛出这个异常。

        Returns:
            AsyncSession: 当前工作单元的数据库会话。
        """
        if self._session is None:
            raise RuntimeError(
                "当前的工作单元还没有被初始化。请确保你使用了正确的格式使用工作单元。"
            )
        return self._session

    async def __aenter__(self) -> Self:
        self._session = self.db_manager.get_session()
        if self.lock:
            await self.lock.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_cal: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()
        await self.session.close()
        self._session = None
        if self.lock is not None:
            self.lock.release()

    @property
    def users(self):
        """用户信息仓库"""

        return UserRepository(self.session)

    @property
    def inventories(self):
        """库存仓库"""

        return InventoryRepository(self.session)

    @property
    def settings(self):
        """设置仓库"""

        return SettingRepository(self.session)

    @property
    def recipes(self):
        """合成配方仓库"""

        return RecipeRepository(self.session)

    @property
    def awards(self):
        """小哥仓库"""

        return AwardRepository(self.session)

    @property
    def skins(self):
        """皮肤仓库"""

        return SkinRepository(self.session)

    @property
    def levels(self):
        """等级仓库"""

        # return LevelRepository()
        return level_repo

    @property
    def skin_inventory(self):
        """皮肤记录仓库"""

        return SkinInventoryRepository(self.session)

    @property
    def money(self):
        return MoneyRepository(self.session)

    @property
    def user_flag(self):
        return UserFlagRepository(self.session)

    @property
    def user_pack(self):
        return UserPackRepository(self.session)

    @property
    def up_pool(self):
        return UpPoolRepository(self.session)


def get_unit_of_work(qqid: str | int | None = None):
    """获得一个工作单元。如果提供了相应的 QQID，可以加锁"""
    lock: asyncio.Lock | None = None
    if qqid is not None:
        lock = get_lock(str(qqid))
    return UnitOfWork(DatabaseManager.get_single(), lock=lock)


__all__ = ["UnitOfWork", "get_unit_of_work"]
