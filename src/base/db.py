"""
和数据库有关的模块
"""

from src.common.config import config


import sqlalchemy
import sqlalchemy.event
from sqlalchemy import PoolProxiedConnection, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


__all__ = ["get_session", "manual_checkpoint", "get_sql_engine", "DatabaseManager"]


class DatabaseManager:
    """
    管理数据库的类，包括连接数据库、创建会话等操作。
    """

    def __init__(
        self,
        database_uri: str = config.sqlalchemy_database_url,
    ):
        """
        初始化数据库管理类
        """
        self.sql_engine = create_async_engine(database_uri)
        self.session_factory = async_sessionmaker(
            self.sql_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        if database_uri.startswith("sqlite+aiosqlite:///"):

            @sqlalchemy.event.listens_for(self.sql_engine.sync_engine, "connect")
            def _(dbapi_connection: PoolProxiedConnection, _):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON;")
                cursor.execute("PRAGMA threading_mode = MULTITHREAD;")
                cursor.execute("PRAGMA busy_timeout = 30000;")
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.close()

    async def manual_checkpoint(self):
        """
        手动为数据库进行一次存档操作。

        在 SQLite3 使用 WAL 模式时，手动对临时文件进行合并的操作因为有些时候会出现一些问题，
        所以需要手动而非依赖自动来保存一直以来积累的数据库更改。
        """
        async with self.sql_engine.connect() as conn:
            await conn.execute(text("PRAGMA wal_checkpoint(FULL);"))
            await conn.commit()

    def get_session(self) -> AsyncSession:
        """获得一个异步可用的数据库会话

        Returns:
            AsyncSession: 数据库会话
        """
        return self.session_factory()

    @staticmethod
    def _get_single() -> "DatabaseManager | None":
        return DatabaseManager.__annotations__.get("instance")

    @staticmethod
    def init_single():
        if DatabaseManager._get_single() is not None:
            raise RuntimeError("请不要重复实例化这个单例")
        DatabaseManager.__annotations__["instance"] = DatabaseManager()

    @staticmethod
    def get_single():
        single = DatabaseManager._get_single()
        if single is None:
            raise RuntimeError("数据库管理对象还没有被初始化")
        return single


def get_session():
    return DatabaseManager.get_single().get_session()


async def manual_checkpoint():
    return await DatabaseManager.get_single().manual_checkpoint()


def get_sql_engine():
    return DatabaseManager.get_single().sql_engine


# 现在还没有形成完整的依赖注入范式，所以，只能先在这里初始化单例，以后再改


DatabaseManager.init_single()
