import datetime
from sqlalchemy import Column, DateTime, Integer


class BaseMixin:
    data_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        index=True,
    )


__all__ = ["BaseMixin"]
