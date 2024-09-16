from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, BaseMixin


class CDKeyBatch(Base, BaseMixin):
    """
    管理一组 CDKey 的元数据
    """

    __tablename__ = "catch_cdk_batch"

    name: Mapped[str] = mapped_column()
    "批次的名称，用于在后台方便管理"

    max_redeem_limit: Mapped[int] = mapped_column(nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class CDKeyBatchAward(Base, BaseMixin):
    """
    储存一个 CDKey 的奖励数据。可以有多个这个的行绑定到
    `catch_cdk` 的一个行上
    """

    __tablename__ = "catch_cdk_batch_award"

    batch_id = Column(Integer, ForeignKey('catch_cdk_batch.data_id', ondelete='CASCADE'))
    aid = Column(Integer, ForeignKey('catch_award.data_id', ondelete='CASCADE'), nullable=True)
    sid = Column(Integer, ForeignKey('catch_skin.data_id', ondelete='CASCADE'), nullable=True)
    chips: Mapped[int] = mapped_column()
    quantity: Mapped[int] = mapped_column(default=1)


class CDKey(Base, BaseMixin):
    """
    储存一个 CDKey 的元数据
    """

    __tablename__ = "catch_cdk"

    code: Mapped[str] = mapped_column(unique=True)
    batch_id = Column(Integer, ForeignKey('catch_cdk_batch.data_id'))


class CDKeyUsage(Base, BaseMixin):
    """
    储存 CDKey 的兑换情况，便于统计等
    """

    __tablename__ = "catch_cdk_usage"

    cdk_id = Column(Integer, ForeignKey('catch_cdk.data_id', ondelete='CASCADE'))
    uid = Column(Integer, ForeignKey("catch_user_data.data_id", ondelete="CASCADE"))
