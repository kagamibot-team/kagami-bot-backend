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

    __table_args__ = (Index("catch_up_pool_rel_index", "aid", "pool_id", unique=True),)

    pool_id = Column(Integer, ForeignKey("catch_up_pool.data_id", ondelete="CASCADE"))
    aid = Column(Integer, ForeignKey("catch_award.data_id", ondelete="CASCADE"))
