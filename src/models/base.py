import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class BaseMixin:
    data_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
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
