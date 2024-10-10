"""
物品系统
"""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, BaseMixin


class ItemInventory(Base, BaseMixin):
    """
    物品库存表
    """

    __tablename__ = "catch_item_inventory"

    item_id: Mapped[str] = mapped_column()
    count: Mapped[int] = mapped_column(default=0, server_default="0")
    stats: Mapped[int] = mapped_column(default=0, server_default="0")
    uid = Column(Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE"))
