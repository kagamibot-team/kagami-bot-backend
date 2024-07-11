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

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

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
    """

    db_manager: DatabaseManager
    _session: AsyncSession | None

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self._session = None

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

    @property
    def users(self):
        """获取用户仓库。

        Returns:
            UserRepository: 用户仓库。
        """

        return UserRepository(self.session)

    @property
    def inventories(self):
        """获取库存仓库。

        Returns:
            InventoryRepository: 库存仓库。
        """

        return InventoryRepository(self.session)

    @property
    def settings(self):
        """获取设置仓库。

        Returns:
            SettingRepository: 设置仓库。
        """

        return SettingRepository(self.session)

    @property
    def recipes(self):
        """获取合成配方仓库。

        Returns:
            RecipeRepository: 合成配方仓库。
        """

        return RecipeRepository(self.session)

    @property
    def awards(self):
        """获取奖励仓库。

        Returns:
            AwardRepository: 奖励仓库。
        """

        return AwardRepository(self.session)

    @property
    def skins(self):
        """获取皮肤仓库。

        Returns:
            SkinRepository: 皮肤仓库。
        """

        return SkinRepository(self.session)


__all__ = ["UnitOfWork"]
