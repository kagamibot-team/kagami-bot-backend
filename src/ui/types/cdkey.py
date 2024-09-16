from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CDKeyBatchMeta(BaseModel):
    batch_id: int
    name: str
    max_redeem_limit: int | None
    expiration_date: datetime | None
    is_active: bool


class CDKeyBatchAwardData(BaseModel):
    """
    对于不同类型，一些量会有不同的处理：

    - 如果是小哥，则两者都启用
    - 如果是皮肤，则会忽略 quantity
    - 如果是薯片，则会忽略 data_id
    """
    award_type: Literal["award", "skin", "chips"]
    data_id: int = 0
    quantity: int = 1
