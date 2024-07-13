class KagamiCoreException(Exception):
    """小镜 Bot 抓小哥游戏的错误类型的基类"""

    def __init__(self) -> None:
        super().__init__()

    @property
    def message(self) -> str:
        return "通常来说，你应该看不到这条错误信息。如果你看到了，请联系开发组修复。"


class NameNotFound(KagamiCoreException):
    """当找不到某个对象时抛出此异常"""

    def __init__(self, obj_type: str, obj_name: str) -> None:
        super().__init__()
        self.obj_type = obj_type
        self.obj_name = obj_name

    @property
    def message(self) -> str:
        return f"我好像不知道你说的 {self.obj_name} 是什么 {self.obj_type}"


class RecipeMissing(KagamiCoreException):
    """在更新配方信息时，因为原配方不存在，所以没办法更新信息"""

    def __init__(self) -> None:
        super().__init__()

    @property
    def message(self) -> str:
        return "原配方不存在，两个参数都要填写"


class ObjectAlreadyExists(Exception):
    """当某个对象已经存在时抛出此异常"""

    pass
