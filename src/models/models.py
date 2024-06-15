import functools
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

    # def __init__(self, catch_interval: float = 3600):
    #     super().__init__(catch_interval=catch_interval)

    catch_interval: Mapped[float] = mapped_column(default=3600)


class Level(Model, BaseMixin):
    """
    小哥等级表
    """

    __tablename__ = "catch_level"

    # def __init__(
    #     self,
    #     name: str = "未命名等级",
    #     weight: float = 0,
    #     color_code: str = "#9e9d95",
    #     price: float = 0,
    # ):
    #     super().__init__(
    #         name=name,
    #         weight=weight,
    #         color_code=color_code,
    #         price=price,
    #     )

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

    # def __init__(self, level: Level, name: str = ""):
    #     super().__init__(
    #         level=level,
    #         name=name,
    #     )

    level_id = Column(Integer, ForeignKey("catch_level.data_id"))
    level: Mapped[Level] = relationship(back_populates="alt_names", lazy="subquery")


class Tag(Model, BaseMixin):
    """
    标签表
    """

    __tablename__ = "catch_tag"

    # def __init__(self, tag_name: str = "", tag_args: str = ""):
    #     super().__init__(
    #         tag_name=tag_name,
    #         tag_args=tag_args,
    #     )

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

    # def __init__(self, level: Level, tag: Tag):
    #     super().__init__(
    #         level=level,
    #         tag=tag,
    #     )

    level_id = Column(Integer, ForeignKey("catch_level.data_id"))
    level: Mapped[Level] = relationship(back_populates="tags", lazy="subquery")

    tag_id = Column(Integer, ForeignKey("catch_tag.data_id"))
    tag: Mapped[Tag] = relationship(back_populates="levels", lazy="subquery")


class Award(Model, BaseMixin):
    __tablename__ = "catch_award"

    # def __init__(
    #     self,
    #     level: Level,
    #     img_path: str = DEFAULT_IMG,
    #     name: str = "",
    #     description: str = "",
    # ):
    #     super().__init__(
    #         level=level,
    #         img_path=img_path,
    #         name=name,
    #         description=description,
    #     )

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

    # def __init__(self, award: Award, name: str = ""):
    #     super().__init__(
    #         award=award,
    #         name=name,
    #     )

    award_id = Column(Integer, ForeignKey("catch_award.data_id"))
    award: Mapped[Award] = relationship(back_populates="alt_names", lazy="subquery")


class AwardTagRelation(Model, BaseMixin):
    """
    一个承载所有小哥的标签关联表
    """

    __tablename__ = "catch_award_tag_relation"

    # def __init__(self, award: Award, tag: Tag):
    #     super().__init__(
    #         award=award,
    #         tag=tag,
    #     )

    award_id = Column(Integer, ForeignKey("catch_award.data_id"))
    award: Mapped[Award] = relationship(back_populates="tags", lazy="subquery")

    tag_id = Column(Integer, ForeignKey("catch_tag.data_id"))
    tag: Mapped[Tag] = relationship(back_populates="awards", lazy="subquery")


class StorageStats(Model, BaseMixin):
    __tablename__ = "catch_award_counter"

    __table_args__ = (
        Index("storage_stat_index", "target_user_id", "target_award_id", unique=True),
    )

    # def __init__(self, user: "User", award: Award, count: int = 0):
    #     super().__init__(
    #         user=user,
    #         award=award,
    #         count=count,
    #     )

    target_user_id = Column(Integer, ForeignKey("catch_user_data.data_id"))
    target_award_id = Column(Integer, ForeignKey("catch_award.data_id"))
    count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="storage_stats", lazy="subquery")
    award: Mapped[Award] = relationship(back_populates="storage_stats", lazy="subquery")


class UsedStats(Model, BaseMixin):
    __tablename__ = "catch_award_stats"

    # def __init__(self, user: "User", award: Award, count: int = 0):
    #     super().__init__(
    #         user=user,
    #         award=award,
    #         count=count,
    #     )

    target_user_id = Column(Integer, ForeignKey("catch_user_data.data_id"))
    target_award_id = Column(Integer, ForeignKey("catch_award.data_id"))
    count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="used_stats", lazy="subquery")
    award: Mapped[Award] = relationship(back_populates="used_stats", lazy="subquery")


class User(Model, BaseMixin):
    __tablename__ = "catch_user_data"

    # def __init__(
    #     self,
    #     qq_id: int,
    #     money: float = 0.0,
    #     pick_count_remain: int = 0,
    #     pick_count_last_calculated: float = 0,
    #     pick_time_delta: float = 7200,
    #     pick_max_cache: int = 1,
    # ):
    #     super().__init__(
    #         qq_id=qq_id,
    #         money=money,
    #         pick_count_remain=pick_count_remain,
    #         pick_count_last_calculated=pick_count_last_calculated,
    #         pick_time_delta=pick_time_delta,
    #         pick_max_cache=pick_max_cache,
    #     )

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

    # def __init__(
    #     self,
    #     user: User,
    #     skin: "Skin",
    # ):
    #     super().__init__(
    #         user=user,
    #         skin=skin,
    #     )

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id"))
    skin_id = Column(Integer, ForeignKey("catch_skin.data_id"))

    user: Mapped[User] = relationship(back_populates="used_skins", lazy="subquery")
    skin: Mapped["Skin"] = relationship(back_populates="used_skins", lazy="subquery")


class OwnedSkin(Model, BaseMixin):
    __tablename__ = "catch_skin_own_record"

    # def __init__(
    #     self,
    #     user: User,
    #     skin: "Skin",
    # ):
    #     super().__init__(
    #         user=user,
    #         skin=skin,
    #     )

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id"))
    skin_id = Column(Integer, ForeignKey("catch_skin.data_id"))

    user: Mapped[User] = relationship(back_populates="owned_skins", lazy="subquery")
    skin: Mapped["Skin"] = relationship(back_populates="owned_skins", lazy="subquery")


class Skin(Model, BaseMixin):
    __tablename__ = "catch_skin"

    # def __init__(
    #     self,
    #     name: str,
    #     award: "Award",
    #     extra_description: str = "",
    #     image: str = DEFAULT_IMG,
    #     price: float = -1.0,
    # ):
    #     super().__init__(
    #         name=name,
    #         award=award,
    #         extra_description=extra_description,
    #         image=image,
    #         price=price,
    #     )

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

    # def __init__(
    #     self,
    #     skin: "Skin",
    #     tag: "Tag",
    # ):
    #     super().__init__(
    #         skin=skin,
    #         tag=tag,
    #     )

    skin_id = Column(Integer, ForeignKey("catch_skin.data_id"))
    tag_id = Column(Integer, ForeignKey("catch_tag.data_id"))
    skin: Mapped[Skin] = relationship(back_populates="tags", lazy="subquery")
    tag: Mapped[Tag] = relationship(back_populates="skins", lazy="subquery")


class SkinAltName(Model, BaseMixin, AltNameMixin):
    """
    一个承载所有皮肤的别名的表
    """

    __tablename__ = "catch_skin_alt_name"

    # def __init__(self, skin: Skin, name: str = ""):
    #     super().__init__(
    #         skin=skin,
    #         name=name,
    #     )

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
