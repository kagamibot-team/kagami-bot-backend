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
    binded_skins: Mapped[list["AwardSkin"]] = relationship(back_populates='applied_award', lazy='subquery')


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
    pick_time_delta: Mapped[float] = mapped_column(default=3600)
    pick_max_cache: Mapped[int] = mapped_column(default=6)

    used_skins: Mapped[list['SkinRecord']] = relationship(back_populates='user', lazy='subquery')
    owned_skins: Mapped[list['SkinOwnRecord']] = relationship(back_populates='user', lazy='subquery')


class SkinRecord(Model, BaseMixin):
    __tablename__ = 'catch_skin_record'

    user_id = Column(Integer, ForeignKey('catch_user_data.data_id'))
    skin_id = Column(Integer, ForeignKey('catch_skin.data_id'))

    user: Mapped[UserData] = relationship(back_populates='used_skins', lazy='subquery')
    skin: Mapped['AwardSkin'] = relationship(back_populates='binded_records', lazy='subquery')


class SkinOwnRecord(Model, BaseMixin):
    __tablename__ = 'catch_skin_own_record'

    user_id = Column(Integer, ForeignKey('catch_user_data.data_id'))
    skin_id = Column(Integer, ForeignKey('catch_skin.data_id'))

    user: Mapped[UserData] = relationship(back_populates='owned_skins', lazy='subquery')
    skin: Mapped['AwardSkin'] = relationship(back_populates='own_records', lazy='subquery')


class AwardSkin(Model, BaseMixin):
    __tablename__ = 'catch_skin'

    name: Mapped[str] = mapped_column(default='')
    extra_description: Mapped[str] = mapped_column(default='')
    image: Mapped[str] = mapped_column(default=DEFAULT_IMG)

    applied_award_id = Column(Integer, ForeignKey('catch_award.data_id'))
    applied_award: Mapped[Award] = relationship(back_populates='binded_skins', lazy='subquery')
    binded_records: Mapped[list[SkinRecord]] = relationship(back_populates='skin', lazy='subquery')
    own_records: Mapped[list[SkinOwnRecord]] = relationship(back_populates='skin', lazy='subquery')
