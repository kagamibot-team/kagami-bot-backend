from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, BaseMixin


class StatRecord(Base, BaseMixin):
    """
    抓小哥的统计数据
    """

    __tablename__ = "catch_stat"

    stat_from = Column(
        Integer,
        ForeignKey("catch_user_data.data_id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    "统计的来源，也就是这个统计的主体玩家。Null 代表这是整个服务器的统计。"

    stat_type: Mapped[str] = mapped_column(index=True)
    "统计的数据的类别"

    count: Mapped[int] = mapped_column(default=0)
    "统计值"

    linked_uid = Column(
        Integer,
        ForeignKey("catch_user_data.data_id", ondelete="CASCADE"),
        nullable=True,
    )
    "统计针对的玩家客体"

    linked_aid = Column(
        Integer,
        ForeignKey("catch_award.data_id", ondelete="CASCADE"),
        nullable=True,
    )
    "统计针对的小哥"

    linked_sid = Column(
        Integer,
        ForeignKey("catch_skin.data_id", ondelete="CASCADE"),
        nullable=True,
    )
    "统计针对的皮肤"

    linked_pid = Column(
        Integer,
        nullable=True,
    )
    "统计针对的猎场"

    linked_rid = Column(
        Integer,
        ForeignKey("catch_recipe.data_id", ondelete="CASCADE"),
        nullable=True,
    )
    "统计针对的合成配方"

    linked_upid = Column(
        Integer,
        ForeignKey("catch_up_pool.data_id", ondelete="CASCADE"),
        nullable=True,
    )
