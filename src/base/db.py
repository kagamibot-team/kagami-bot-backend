import sqlalchemy
import sqlalchemy.event
from sqlalchemy import PoolProxiedConnection, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.common.config import config

sqlEngine = create_async_engine(config.sqlalchemy_database_url)

_async_session_factory = async_sessionmaker(
    sqlEngine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

if config.sqlalchemy_database_url.startswith("sqlite+aiosqlite:///"):
    @sqlalchemy.event.listens_for(sqlEngine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: PoolProxiedConnection, _):
        """
        为 SQLite3 添加优化
        """

        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA threading_mode = MULTITHREAD;")
        cursor.execute("PRAGMA busy_timeout = 30000;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()


async def manual_checkpoint(engine: AsyncEngine = sqlEngine):
    async with engine.connect() as conn:
        await conn.execute(text("PRAGMA wal_checkpoint(FULL);"))
        await conn.commit()


def get_session():
    return _async_session_factory()


__all__ = ["get_session", "sqlEngine"]
