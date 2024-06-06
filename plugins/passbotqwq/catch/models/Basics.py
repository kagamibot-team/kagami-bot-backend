import os
from nonebot_plugin_orm import Model
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .BaseMixin import BaseMixin


DEFAULT_IMG = os.path.join(".", "res", "catch", "default.png")


class Level(Model, BaseMixin):
    __tablename__ = 'catch_level'

    name: Mapped[str] = mapped_column(default="未命名等级", unique=True)
    weight: Mapped[float] = mapped_column(default=0)

    level_color_code: Mapped[str] = mapped_column(default="#9e9d95")

    awards: Mapped[set["Award"]] = relationship(back_populates="level", lazy="subquery")


class Award(Model, BaseMixin):
    __tablename__ = 'catch_award'

    img_path: Mapped[str] = mapped_column(default=DEFAULT_IMG)
    name: Mapped[str] = mapped_column(default="名称已丢失", unique=True)
    description: Mapped[str] = mapped_column(default="这只小哥还没有描述，它只是静静地躺在这里，等待着别人给他下定义。")

    level_id = Column(Integer, ForeignKey('catch_level.data_id'))
    level: Mapped[Level] = relationship(back_populates="awards", lazy="subquery")
    binded_counters: Mapped[list["AwardCountStorage"]] = relationship(back_populates="target_award", lazy="subquery")


class AwardCountStorage(Model, BaseMixin):
    __tablename__ = 'catch_award_counter'

    target_user_id = Column(Integer, ForeignKey('catch_user_data.data_id'))
    target_award_id = Column(Integer, ForeignKey('catch_award.data_id'))

    target_user: Mapped["UserData"] = relationship(back_populates="award_counters", lazy="subquery")
    target_award: Mapped[Award] = relationship(back_populates="binded_counters", lazy="subquery")
    
    award_count: Mapped[int] = mapped_column(default=0)


class UserData(Model, BaseMixin):
    __tablename__ = 'catch_user_data'

    qq_id: Mapped[int] = mapped_column(unique=True)

    award_counters: Mapped[list[AwardCountStorage]] = relationship(back_populates='target_user', lazy="subquery")
    money: Mapped[float] = mapped_column(default=0.0)

    pick_count_remain: Mapped[int] = mapped_column(default=0)
    pick_count_last_calculated: Mapped[float] = mapped_column(default=0)
