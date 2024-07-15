from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, BaseMixin


class RecipeHistory(Base, BaseMixin):
    """
    合成小哥的历史记录
    """

    __tablename__ = "catch_recipe_history"

    source: Mapped[str] = mapped_column(index=True)
    "这条合成的来源，一般请在这里填入 QQ 群号"

    recipe = Column(
        Integer, ForeignKey("catch_recipe.data_id", ondelete="CASCADE"), index=True
    )
    "合成配方的 ID"

    first = Column(Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE"))
    "第一个发现这个配方的人"
