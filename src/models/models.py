import hashlib
import os
import random
from collections.abc import Hashable

from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import *
from .item import ItemInventory
from .stats import StatRecord
from .up_pool import UpPool


class Global(Base, BaseMixin):
    """
    全局变量表
    """

    __tablename__ = "catch_global"

    catch_interval: Mapped[float] = mapped_column(default=3600)
    last_reported_version: Mapped[str] = mapped_column(default="", server_default="")
    opened_pack: Mapped[int] = mapped_column(default=1, server_default="1")


class Award(Base, BaseMixin):
    __tablename__ = "catch_award"

    name: Mapped[str] = mapped_column(default="", unique=True, index=True)
    description: Mapped[str] = mapped_column(default="")
    sorting: Mapped[int] = mapped_column(default=0)
    level_id = Column(Integer, index=True)
    main_pack_id = Column(Integer, index=True, default=1, server_default="1")


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

    chips: Mapped[float] = mapped_column(default=0.0)
    biscuit: Mapped[int] = mapped_column(default=0, server_default="0")

    slot_empty: Mapped[int] = mapped_column(default=0)
    slot_last_time: Mapped[float] = mapped_column(default=0)
    slot_count: Mapped[int] = mapped_column(default=1)

    # 20240622 追加
    # 和签到有关的两个字段
    sign_last_time: Mapped[float] = mapped_column(default=0, server_default="0")
    sign_count: Mapped[int] = mapped_column(default=0, server_default="0")

    # Feature flag: 未来可能会启用的若干项，现在先开个字段
    flags: Mapped[str] = mapped_column(default="", server_default="")

    # 20240704 追加
    # 和早睡有关的两个字段
    sleep_last_time: Mapped[float] = mapped_column(default=0, server_default="0")
    sleep_count: Mapped[int] = mapped_column(default=0, server_default="0")
    get_up_time: Mapped[float] = mapped_column(default=0, server_default="0")

    # 20240729 追加
    # 用户的特殊称呼不再在配置文件中设置，太麻烦了
    special_call: Mapped[str] = mapped_column(default="", server_default="")

    using_pid: Mapped[int] = mapped_column(default=1, server_default="1")
    "用户正在使用的猎场"

    using_up_pool = Column(
        Integer,
        ForeignKey("catch_up_pool.data_id", ondelete="SET NULL"),
        nullable=True,
    )
    "用户挂载的猎场升级，可能为空"

    own_packs: Mapped[str] = mapped_column(default="1", server_default="'1'")
    "用户有哪些猎场"


class SkinRecord(Base, BaseMixin):
    __tablename__ = "catch_skin_inventory"

    user_id = Column(Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE"))
    skin_id = Column(Integer, ForeignKey("catch_skin.data_id", ondelete="CASCADE"))
    selected = Column(Integer, default=0, server_default="0")


class Skin(Base, BaseMixin):
    __tablename__ = "catch_skin"

    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(default="")
    price: Mapped[float] = mapped_column(default=-1.0)
    aid = Column(Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"))


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
    def get_random_object(
        a1: int, a2: int, a3: int, salt: Hashable = None
    ) -> random.Random:
        """获得一个合成配方组的 Random 对象

        Args:
            a1 (int): 第一个小哥
            a2 (int): 第二个小哥
            a3 (int): 第三个小哥
        """

        return random.Random(hashlib.md5(str((a1, a2, a3, salt)).encode()).hexdigest())


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
    "UpPool",
    "StatRecord",
    "ItemInventory",
]
