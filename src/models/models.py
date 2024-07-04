import datetime
import os
import random
import struct

from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import *

DEFAULT_IMG = os.path.join(".", "res", "default.png")


class Global(Base, BaseMixin):
    """
    全局变量表
    """

    __tablename__ = "catch_global"

    catch_interval: Mapped[float] = mapped_column(default=3600)
    last_reported_version: Mapped[str] = mapped_column(default="", server_default="")


class Level(Base, BaseMixin):
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


class LevelAltName(Base, BaseMixin, AltNameMixin):
    """
    一个承载所有等级的别名的表
    """

    __tablename__ = "catch_level_alt_name"

    level_id = Column(Integer, ForeignKey("catch_level.data_id", ondelete="CASCADE"))
    level: Mapped[Level] = relationship(back_populates="alt_names", lazy="subquery")


class Tag(Base, BaseMixin):
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


class LevelTagRelation(Base, BaseMixin):
    """
    等级标签关联表
    """

    __tablename__ = "catch_level_tag_relation"

    level_id = Column(Integer, ForeignKey("catch_level.data_id", ondelete="CASCADE"))
    level: Mapped[Level] = relationship(back_populates="tags", lazy="subquery")

    tag_id = Column(Integer, ForeignKey("catch_tag.data_id", ondelete="CASCADE"))
    tag: Mapped[Tag] = relationship(back_populates="levels", lazy="subquery")


class Award(Base, BaseMixin):
    __tablename__ = "catch_award"

    img_path: Mapped[str] = mapped_column(default=DEFAULT_IMG)
    name: Mapped[str] = mapped_column(default="", unique=True, index=True)
    description: Mapped[str] = mapped_column(default="")
    sorting_priority: Mapped[int] = mapped_column(default=0)

    level_id = Column(
        Integer, ForeignKey("catch_level.data_id", ondelete="CASCADE"), index=True
    )
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

    tags: Mapped[list["AwardTagRelation"]] = relationship(
        back_populates="award", lazy="subquery"
    )

    catch_group = Column(
        Integer,
        ForeignKey("catch_catch_group.data_id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    is_special_get_only: Mapped[bool] = mapped_column(default=False, server_default="0")


class AwardAltName(Base, BaseMixin, AltNameMixin):
    """
    一个承载所有小哥的别名的表
    """

    __tablename__ = "catch_award_alt_name"

    award_id = Column(
        Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"), index=True
    )
    award: Mapped[Award] = relationship(back_populates="alt_names", lazy="subquery")


class AwardTagRelation(Base, BaseMixin):
    """
    一个承载所有小哥的标签关联表
    """

    __tablename__ = "catch_award_tag_relation"

    award_id = Column(Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"))
    award: Mapped[Award] = relationship(back_populates="tags", lazy="subquery")

    tag_id = Column(Integer, ForeignKey("catch_tag.data_id", ondelete="CASCADE"))
    tag: Mapped[Tag] = relationship(back_populates="awards", lazy="subquery")


class StorageStats(Base, BaseMixin):
    __tablename__ = "catch_award_counter"

    __table_args__ = (
        Index("storage_stat_index", "target_user_id", "target_award_id", unique=True),
    )

    target_user_id = Column(
        Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE")
    )
    target_award_id = Column(
        Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE")
    )
    count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="storage_stats", lazy="subquery")
    award: Mapped[Award] = relationship(back_populates="storage_stats", lazy="subquery")


class UsedStats(Base, BaseMixin):
    __tablename__ = "catch_award_stats"

    target_user_id = Column(
        Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE")
    )
    target_award_id = Column(
        Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE")
    )
    count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="used_stats", lazy="subquery")
    award: Mapped[Award] = relationship(back_populates="used_stats", lazy="subquery")


class User(Base, BaseMixin):
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

    # 20240622 追加
    # 和签到有关的两个字段
    last_sign_in_time: Mapped[float] = mapped_column(default=0, server_default="0")
    sign_in_count: Mapped[int] = mapped_column(default=0, server_default="0")

    # Feature flag: 未来可能会启用的若干项，现在先开个字段
    feature_flag: Mapped[str] = mapped_column(default="", server_default="")

    # 20240704 追加
    # 和早睡有关的两个字段
    last_sleep_early_time: Mapped[float] = mapped_column(default=0, server_default="0")
    sleep_early_count: Mapped[int] = mapped_column(default=0, server_default="0")


class UsedSkin(Base, BaseMixin):
    __tablename__ = "catch_skin_record"

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE"))
    skin_id = Column(Integer, ForeignKey("catch_skin.data_id", ondelete="CASCADE"))

    user: Mapped[User] = relationship(back_populates="used_skins", lazy="subquery")
    skin: Mapped["Skin"] = relationship(back_populates="used_skins", lazy="subquery")


class OwnedSkin(Base, BaseMixin):
    __tablename__ = "catch_skin_own_record"

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE"))
    skin_id = Column(Integer, ForeignKey("catch_skin.data_id", ondelete="CASCADE"))

    user: Mapped[User] = relationship(back_populates="owned_skins", lazy="subquery")
    skin: Mapped["Skin"] = relationship(back_populates="owned_skins", lazy="subquery")


class Skin(Base, BaseMixin):
    __tablename__ = "catch_skin"

    name: Mapped[str] = mapped_column()
    extra_description: Mapped[str] = mapped_column(default="")
    image: Mapped[str] = mapped_column(default=DEFAULT_IMG)
    price: Mapped[float] = mapped_column(default=-1.0)
    applied_award_id = Column(
        Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE")
    )

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


class SkinTagRelation(Base, BaseMixin):
    __tablename__ = "catch_skin_tag_relation"

    skin_id = Column(Integer, ForeignKey("catch_skin.data_id", ondelete="CASCADE"))
    tag_id = Column(Integer, ForeignKey("catch_tag.data_id", ondelete="CASCADE"))
    skin: Mapped[Skin] = relationship(back_populates="tags", lazy="subquery")
    tag: Mapped[Tag] = relationship(back_populates="skins", lazy="subquery")


class SkinAltName(Base, BaseMixin, AltNameMixin):
    """
    一个承载所有皮肤的别名的表
    """

    __tablename__ = "catch_skin_alt_name"

    skin_id = Column(Integer, ForeignKey("catch_skin.data_id", ondelete="CASCADE"))
    skin: Mapped[Skin] = relationship(back_populates="alt_names", lazy="subquery")


class CatchGroup(Base, BaseMixin):
    """
    抓小哥时所应用的概率组，将在未来启用
    """

    __tablename__ = "catch_catch_group"

    weight: Mapped[float] = mapped_column(default=0.0, server_default="0")
    time_limit_rule: Mapped[str] = mapped_column(default="* * * * * * *")

    @staticmethod
    def validate_single_simple(rule: str, val: int) -> bool:
        if rule == "*":
            return True

        if "-" not in rule:
            return str(val) == rule

        rs = rule.split("-")
        if len(rs) != 2:
            return False

        l, r = rs
        if not l.isdigit() or not r.isdigit():
            return False
        return int(l) <= val <= int(r)

    @staticmethod
    def validate_single(rule: str, val: int) -> bool:
        rs = rule.split(",")

        for r in rs:
            if CatchGroup.validate_single_simple(r, val):
                return True

        return False

    @staticmethod
    def validate(rule: str, time: datetime.datetime) -> bool:
        rs = rule.split(" ")
        if len(rs) != 7:
            return False

        Y, M, D, d, h, m, s = rs

        if not CatchGroup.validate_single(Y, time.year):
            return False
        if not CatchGroup.validate_single(M, time.month):
            return False
        if not CatchGroup.validate_single(D, time.day):
            return False
        if not CatchGroup.validate_single(d, time.weekday()):
            return False
        if not CatchGroup.validate_single(h, time.hour):
            return False
        if not CatchGroup.validate_single(m, time.minute):
            return False
        if not CatchGroup.validate_single(s, time.second):
            return False

        return True


class Recipe(Base, BaseMixin):
    """已经被记录下来的合成配方，是一个无序配方"""

    __tablename__ = "catch_recipe"

    __table_args__ = (
        Index("catch_recipe_index", "award1", "award2", "award3", unique=True),
    )

    award1 = Column(Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"))
    award2 = Column(Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"))
    award3 = Column(Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"))

    possibility: Mapped[float] = mapped_column()

    result = Column(
        Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"), index=True
    )

    @staticmethod
    def get_random_object(a1: int, a2: int, a3: int) -> random.Random:
        """获得一个合成配方组的 Random 对象

        Args:
            a1 (int): 第一个小哥
            a2 (int): 第二个小哥
            a3 (int): 第三个小哥
        """

        return random.Random(hash((a1, a2, a3)))


__all__ = [
    "Base",
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
    "CatchGroup",
    "Recipe",
]
