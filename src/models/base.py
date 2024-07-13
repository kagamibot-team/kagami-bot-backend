import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base

from src.common.times import now_datetime


Base = declarative_base()

if TYPE_CHECKING:

    class Base(DeclarativeBase):
        pass


class BaseMixin:
    data_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=now_datetime)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=now_datetime,
        onupdate=now_datetime,
    )


class AltNameMixin:
    name: Mapped[str] = mapped_column(unique=True, index=True)


class TagsMixin:
    tags: Mapped[str] = mapped_column(default="")

    def getTags(self) -> set[str]:
        return set(e for e in self.tags.split(" ") if len(e) > 0)

    def setTags(self, tags: set[str]):
        self.tags = " ".join(tags)


__all__ = ["BaseMixin", "AltNameMixin", "TagsMixin", "Base"]
