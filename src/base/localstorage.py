import json
from pathlib import Path
from types import TracebackType
from typing import Any, Generic, Optional, TypeVar

from loguru import logger
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class LocalStorage:
    """
    本地储存类，用于储存一些全局状态。
    注意，这里的操作可能会比较缓慢，所以请不要用它来储存*任何*比较庞大的数据结构，
    例如列表等。
    """

    data: dict[str, dict[str, Any]]
    path: Path

    def __init__(self, path: Path) -> None:
        """初始化本地持久储存

        Args:
            path (Path): 持久化存储的文件地址。建议是一个 `.json` 文件
        """
        self.data = {}
        self.path = path
        assert path.name, "提供的地址应该有一个文件名"
        self.load()

    def load(self):
        """尝试从文件中读取数据"""

        try:
            with open(self.path, "r") as f:
                data = json.load(f)
                self.data = data
        except FileNotFoundError:
            self.write()
        except json.JSONDecodeError:
            logger.warning("读取 JSON 数据时出错")
            self.write()

    def write(self):
        """
        将当前的数据写入到持久化文件中
        """
        if not self.path.parent.exists():
            self.path.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f)

    def get_item(self, key: str, cls: type[T], allow_overwrite: bool = False) -> T:
        """获得一个元素

        Args:
            key (str): 这个元素的键
            cls (type[T]): Pydantic 模型
            allow_overwrite (bool, optional): 是否允许在出错时重写。如果不允许，则会抛出错误

        Returns:
            T:  得到的 Pydantic Model 对象。
                注意，当你更改这个对象时，不会直接影响到储存的持久化数据本身。
                所以，如果你需要更改数据，你需要将更改后的数据用相应方法覆盖。

                ```python
                data = local_storage.get_item("test", TestModel)
                data.test_value = True
                local_storage.set_item("test", data)
                ```
        """
        self.load()
        val = self.data.get(key, {})
        try:
            return cls.model_validate(val, strict=True)
        except ValidationError as e:
            logger.warning(f"在验证数据时出错：{e}")
            if allow_overwrite or key not in self.data:
                data = cls()
                self.data[key] = data.model_dump()
                return data
            else:
                raise e from e

    def set_item(self, key: str, val: BaseModel | dict[str, Any]):
        """设置 LocalStorage 的值

        Args:
            key (str): 键
            val (BaseModel | dict[str, Any]): 值
        """
        if isinstance(val, BaseModel):
            val = val.model_dump()
        self.data[key] = val
        self.write()

    def context(
        self, key: str, cls: type[T], allow_overwrite: bool = False
    ) -> "LocalStorageContext[T]":
        """获得一个用于更改数据的上下文

        Args:
            key (str): 键
            cls (type[T]): Pydantic 类型
            allow_overwrite (bool, optional): 是否允许在出错时覆盖数据

        Returns:
            LocalStorageContext[T]: 一个上下文。你可以使用 `with` 语法来编辑值：

            ```python
            with local_storage.context("test", TestModel) as data:
                data.value = True
            ```

            这样会自动将更改更新并写入文件。
        """
        return LocalStorageContext(
            data=self.get_item(key, cls, allow_overwrite),
            parent=self,
            parent_key=key,
        )


class LocalStorageContext(Generic[T]):
    """
    持久化数据的上下文管理
    """

    def __init__(self, data: T, parent: LocalStorage, parent_key: str) -> None:
        self.data = data
        self.parent = parent
        self.parent_key = parent_key

    def __enter__(self):
        return self.data

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_inst: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        if exc_type is None and exc_inst is None and exc_tb is None:
            self.parent.set_item(self.parent_key, self.data)

        # 代表该异常将会向外传播
        return False
