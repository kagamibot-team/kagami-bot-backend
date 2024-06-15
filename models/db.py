from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import config


_engine = create_async_engine(config.sqlalchemy_database_url)

_async_session_factory = async_sessionmaker(
    _engine, class_=AsyncSession, expire_on_commit=True
)


def get_session():
    return _async_session_factory()


__all__ = ["get_session"]
