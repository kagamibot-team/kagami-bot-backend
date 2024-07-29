import os
import random

from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import *
from .recipe_history import RecipeHistory

DEFAULT_IMG = os.path.join(".", "res", "default.png")


class Global(Base, BaseMixin):
    """
    全局变量表
    """

    __tablename__ = "catch_global"

    catch_interval: Mapped[float] = mapped_column(default=3600)
    last_reported_version: Mapped[str] = mapped_column(default="", server_default="")


class Award(Base, BaseMixin):
    __tablename__ = "catch_award"

    image: Mapped[str] = mapped_column(default=DEFAULT_IMG)
    name: Mapped[str] = mapped_column(default="", unique=True, index=True)
    description: Mapped[str] = mapped_column(default="")
    sorting: Mapped[int] = mapped_column(default=0)
    level_id = Column(Integer, index=True)
    is_special_get_only: Mapped[bool] = mapped_column(default=False, server_default="0")


class AwardAltName(Base, BaseMixin, AltNameMixin):
    """
    一个承载所有小哥的别名的表
    """

    __tablename__ = "catch_award_alt_name"

    award_id = Column(
        Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"), index=True
    )


class Inventory(Base, BaseMixin):
    __tablename__ = "catch_inventory"

    __table_args__ = (Index("storage_stat_index", "user_id", "award_id", unique=True),)

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE"))
    award_id = Column(Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"))
    storage: Mapped[int] = mapped_column(default=0)
    used: Mapped[int] = mapped_column(default=0)


class User(Base, BaseMixin):
    __tablename__ = "catch_user_data"

    qq_id: Mapped[str] = mapped_column(unique=True, index=True)
    money: Mapped[float] = mapped_column(default=0.0)

    pick_count_remain: Mapped[int] = mapped_column(default=0)
    pick_count_last_calculated: Mapped[float] = mapped_column(default=0)
    pick_time_delta: Mapped[float] = mapped_column(default=7200)
    pick_max_cache: Mapped[int] = mapped_column(default=1)

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

    # 20240729 追加
    # 用户的特殊称呼不再在配置文件中设置，太麻烦了
    special_call: Mapped[str] = mapped_column(default="", server_default="")


class SkinRecord(Base, BaseMixin):
    __tablename__ = "catch_skin_inventory"

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE"))
    skin_id = Column(Integer, ForeignKey("catch_skin.data_id", ondelete="CASCADE"))
    selected = Column(Integer, default=0, server_default="0")


class Skin(Base, BaseMixin):
    __tablename__ = "catch_skin"

    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(default="")
    image: Mapped[str] = mapped_column(default=DEFAULT_IMG)
    price: Mapped[float] = mapped_column(default=-1.0)
    award_id = Column(Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"))


class SkinAltName(Base, BaseMixin, AltNameMixin):
    """
    一个承载所有皮肤的别名的表
    """

    __tablename__ = "catch_skin_alt_name"

    skin_id = Column(Integer, ForeignKey("catch_skin.data_id", ondelete="CASCADE"))


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
    modified = Column(Integer, default=0, server_default="0")

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
    "Global",
    "Award",
    "AwardAltName",
    "Inventory",
    "User",
    "SkinRecord",
    "Skin",
    "SkinAltName",
    "Recipe",
    "RecipeHistory",
]
