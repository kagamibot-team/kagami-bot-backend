"""
后端将数据暴露给前端的接口定义，以及将模板显示出来的定义
"""

import uuid

from pydantic import BaseModel


class BackendDataManager:
    data: dict[str, BaseModel]

    def __init__(self) -> None:
        self.data = {}

    def register(self, data: BaseModel) -> str:
        """
        往数据管理器中注册一些数据，返回这个数据的识别 ID
        """
        _id = uuid.uuid4().hex
        self.data[_id] = data
        return _id

    def get(self, data_id: str) -> BaseModel | None:
        """
        获得数据
        """
        return self.data.get(data_id, None)
