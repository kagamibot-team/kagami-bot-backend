import os
from nonebot_plugin_orm import Model
from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mixins import *


DEFAULT_IMG = os.path.join(".", "res", "default.png")


class Global(Model, BaseMixin):
    """
    全局变量表
    """

    __tablename__ = "catch_global"

    catch_interval: Mapped[float] = mapped_column(default=3600)


class Level(Model, BaseMixin):
    """
    小哥等级表
    """

    __tablename__ = "catch_level"

    name: Mapped[str] = mapped_column(default="未命名等级", unique=True)
    sorting_priority: Mapped[int] = mapped_column(default=0)
    weight: Mapped[float] = mapped_column(default=0)
    color_code: Mapped[str] = mapped_column(default="#9e9d95")
    awards: Mapped[set["Award"]] = relationship(back_populates="level", lazy="subquery")
    price: Mapped[float] = mapped_column(default=0)

    alt_names: Mapped[list["LevelAltName"]] = relationship(
        back_populates="level", lazy="subquery"
    )

    tags: Mapped[list["LevelTagRelation"]] = relationship(
        back_populates="level", lazy="subquery"
    )


class LevelAltName(Model, BaseMixin, AltNameMixin):
    """
    一个承载所有等级的别名的表
    """

    __tablename__ = "catch_level_alt_name"

    level_id = Column(Integer, ForeignKey("catch_level.data_id"))
    level: Mapped[Level] = relationship(back_populates="alt_names", lazy="subquery")


class Tag(Model, BaseMixin):
    """
    标签表
    """

    __tablename__ = "catch_tag"

    tag_name: Mapped[str] = mapped_column(default="")
    tag_args: Mapped[str] = mapped_column(default="")

    levels: Mapped[list["LevelTagRelation"]] = relationship(
        back_populates="tag", lazy="subquery"
    )
    awards: Mapped[list["AwardTagRelation"]] = relationship(
        back_populates="tag", lazy="subquery"
    )
    skins: Mapped[list["SkinTagRelation"]] = relationship(
        back_populates="tag", lazy="subquery"
    )


class LevelTagRelation(Model, BaseMixin):
    """
    等级标签关联表
    """

    __tablename__ = "catch_level_tag_relation"

    level_id = Column(Integer, ForeignKey("catch_level.data_id"))
    level: Mapped[Level] = relationship(back_populates="tags", lazy="subquery")

    tag_id = Column(Integer, ForeignKey("catch_tag.data_id"))
    tag: Mapped[Tag] = relationship(back_populates="levels", lazy="subquery")


class Award(Model, BaseMixin):
    __tablename__ = "catch_award"

    img_path: Mapped[str] = mapped_column(default=DEFAULT_IMG)
    name: Mapped[str] = mapped_column(default="", unique=True)
    description: Mapped[str] = mapped_column(default="")
    sorting_priority: Mapped[int] = mapped_column(default=0)

    level_id = Column(Integer, ForeignKey("catch_level.data_id"), index=True)
    level: Mapped[Level] = relationship(back_populates="awards", lazy="subquery")

    storage_stats: Mapped[list["StorageStats"]] = relationship(
        back_populates="award", lazy="subquery"
    )
    used_stats: Mapped[list["UsedStats"]] = relationship(
        back_populates="award", lazy="subquery"
    )
    skins: Mapped[list["Skin"]] = relationship(back_populates="award", lazy="subquery")

    alt_names: Mapped[list["AwardAltName"]] = relationship(
        back_populates="award", lazy="subquery"
    )

    tags: Mapped[list["AwardTagRelation"]] = relationship(back_populates="award", lazy="subquery")


class AwardAltName(Model, BaseMixin, AltNameMixin):
    """
    一个承载所有小哥的别名的表
    """

    __tablename__ = "catch_award_alt_name"

    award_id = Column(Integer, ForeignKey("catch_award.data_id"))
    award: Mapped[Award] = relationship(back_populates="alt_names", lazy="subquery")


class AwardTagRelation(Model, BaseMixin):
    """
    一个承载所有小哥的标签关联表
    """

    __tablename__ = "catch_award_tag_relation"

    award_id = Column(Integer, ForeignKey("catch_award.data_id"))
    award: Mapped[Award] = relationship(back_populates="tags", lazy="subquery")

    tag_id = Column(Integer, ForeignKey("catch_tag.data_id"))
    tag: Mapped[Tag] = relationship(back_populates="awards", lazy="subquery")


class StorageStats(Model, BaseMixin):
    __tablename__ = "catch_award_counter"

    __table_args__ = (
        Index("storage_stat_index", "target_user_id", "target_award_id", unique=True),
    )

    target_user_id = Column(Integer, ForeignKey("catch_user_data.data_id"))
    target_award_id = Column(Integer, ForeignKey("catch_award.data_id"))
    count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="storage_stats", lazy="subquery")
    award: Mapped[Award] = relationship(back_populates="storage_stats", lazy="subquery")


class UsedStats(Model, BaseMixin):
    __tablename__ = "catch_award_stats"

    target_user_id = Column(Integer, ForeignKey("catch_user_data.data_id"))
    target_award_id = Column(Integer, ForeignKey("catch_award.data_id"))
    count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="used_stats", lazy="subquery")
    award: Mapped[Award] = relationship(back_populates="used_stats", lazy="subquery")


class User(Model, BaseMixin):
    __tablename__ = "catch_user_data"

    qq_id: Mapped[str] = mapped_column(unique=True, index=True)

    storage_stats: Mapped[list[StorageStats]] = relationship(
        back_populates="user", lazy="subquery"
    )
    used_stats: Mapped[list[UsedStats]] = relationship(
        back_populates="user", lazy="subquery"
    )
    money: Mapped[float] = mapped_column(default=0.0)

    pick_count_remain: Mapped[int] = mapped_column(default=0)
    pick_count_last_calculated: Mapped[float] = mapped_column(default=0)
    pick_time_delta: Mapped[float] = mapped_column(default=7200)
    pick_max_cache: Mapped[int] = mapped_column(default=1)

    used_skins: Mapped[list["UsedSkin"]] = relationship(
        back_populates="user", lazy="subquery"
    )
    owned_skins: Mapped[list["OwnedSkin"]] = relationship(
        back_populates="user", lazy="subquery"
    )


class UsedSkin(Model, BaseMixin):
    __tablename__ = "catch_skin_record"

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id"))
    skin_id = Column(Integer, ForeignKey("catch_skin.data_id"))

    user: Mapped[User] = relationship(back_populates="used_skins", lazy="subquery")
    skin: Mapped["Skin"] = relationship(back_populates="used_skins", lazy="subquery")


class OwnedSkin(Model, BaseMixin):
    __tablename__ = "catch_skin_own_record"

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id"))
    skin_id = Column(Integer, ForeignKey("catch_skin.data_id"))

    user: Mapped[User] = relationship(back_populates="owned_skins", lazy="subquery")
    skin: Mapped["Skin"] = relationship(back_populates="owned_skins", lazy="subquery")


class Skin(Model, BaseMixin):
    __tablename__ = "catch_skin"

    name: Mapped[str] = mapped_column()
    extra_description: Mapped[str] = mapped_column(default="")
    image: Mapped[str] = mapped_column(default=DEFAULT_IMG)
    price: Mapped[float] = mapped_column(default=-1.0)
    applied_award_id = Column(Integer, ForeignKey("catch_award.data_id"))

    award: Mapped[Award] = relationship(back_populates="skins", lazy="subquery")
    used_skins: Mapped[list[UsedSkin]] = relationship(
        back_populates="skin", lazy="subquery"
    )
    owned_skins: Mapped[list[OwnedSkin]] = relationship(
        back_populates="skin", lazy="subquery"
    )

    alt_names: Mapped[list["SkinAltName"]] = relationship(
        back_populates="skin", lazy="subquery"
    )

    tags: Mapped[list["SkinTagRelation"]] = relationship(
        back_populates="skin", lazy="subquery"
    )


class SkinTagRelation(Model, BaseMixin):
    __tablename__ = "catch_skin_tag_relation"

    skin_id = Column(Integer, ForeignKey("catch_skin.data_id"))
    tag_id = Column(Integer, ForeignKey("catch_tag.data_id"))
    skin: Mapped[Skin] = relationship(back_populates="tags", lazy="subquery")
    tag: Mapped[Tag] = relationship(back_populates="skins", lazy="subquery")


class SkinAltName(Model, BaseMixin, AltNameMixin):
    """
    一个承载所有皮肤的别名的表
    """

    __tablename__ = "catch_skin_alt_name"

    skin_id = Column(Integer, ForeignKey("catch_skin.data_id"))
    skin: Mapped[Skin] = relationship(back_populates="alt_names", lazy="subquery")


__all__ = [
    "Global",
    "Level",
    "LevelAltName",
    "Award",
    "AwardAltName",
    "StorageStats",
    "UsedStats",
    "User",
    "UsedSkin",
    "OwnedSkin",
    "Skin",
    "SkinAltName",
    "Tag",
    "SkinTagRelation",
    "LevelTagRelation",
    "AwardTagRelation",
]
