from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, BaseMixin


class UpPool(Base, BaseMixin):
    """
    Up 池
    """

    __tablename__ = "catch_up_pool"

    belong_pack: Mapped[int] = mapped_column(default=1)
    "属于哪个猎场"

    display: Mapped[int] = mapped_column(default=0)
    "是否展示出来"

    enabled: Mapped[bool] = mapped_column(default=False)
    "给不给玩家挂载"

    cost: Mapped[int] = mapped_column(default=0)
    "买下这个 Up 池需要多少薯片"

    name: Mapped[str] = mapped_column(default="", index=True)
    "Up 池的名字"


class UpPoolAwardRelationship(Base, BaseMixin):
    """
    Up 池和小哥的多对多关系，记录 Up 池容纳的小哥
    """

    __tablename__ = "catch_up_pool_relationship"

    pool_id = Column(
        Integer,
        ForeignKey("catch_up_pool.data_id", ondelete="CASCADE"),
        index=True,
    )
    aid = Column(
        Integer,
        ForeignKey("catch_award.data_id", ondelete="CASCADE"),
    )


class UpPoolInventory(Base, BaseMixin):
    """
    用户和猎场升级之间的关系
    """

    __tablename__ = "catch_up_pool_inventory"
    __table_args__ = (
        Index("catch_up_pool_inventory_index", "uid", "pool_id", unique=True),
    )

    uid = Column(
        Integer,
        ForeignKey("catch_user_data.data_id", ondelete="CASCADE"),
        index=True,
    )
    pool_id = Column(
        Integer,
        ForeignKey("catch_up_pool.data_id", ondelete="CASCADE"),
        index=True,
    )


class PackAwardRelationship(Base, BaseMixin):
    """
    猎场和小哥的多对多关系，记录猎场容纳的小哥。
    就是说，这里记录的是，一个猎场，除了主猎场在这个猎场的小哥，
    还有哪些小哥需要记录。
    """

    __tablename__ = "catch_pack_award_relationship"

    pack: Mapped[int] = mapped_column(index=True)
    aid = Column(
        Integer,
        ForeignKey("catch_award.data_id", ondelete="CASCADE"),
        index=True,
    )
