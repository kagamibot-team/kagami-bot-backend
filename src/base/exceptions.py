class KagamiCoreException(Exception):
    """小镜 Bot 抓小哥游戏的错误类型的基类"""

    @property
    def message(self) -> str:
        return "通常来说，你应该看不到这条错误信息。如果你看到了，请联系开发组修复。"

    def __str__(self) -> str:
        return self.message


class ObjectNotFoundException(KagamiCoreException):
    """当找不到某个对象时抛出此异常"""

    def __init__(self, obj_type: str, obj_name: str) -> None:
        super().__init__()
        self.obj_type = obj_type
        self.obj_name = obj_name

    @property
    def message(self) -> str:
        return f"我好像没找到你说的 {self.obj_name} 的那个 {self.obj_type}"


class RecipeMissingException(KagamiCoreException):
    """在更新配方信息时，因为原配方不存在，所以没办法更新信息"""

    @property
    def message(self) -> str:
        return "原配方不存在，两个参数都要填写"


class ObjectAlreadyExistsException(KagamiCoreException):
    """当某个对象已经存在时抛出此异常"""

    def __init__(self, obj_name: str | None) -> None:
        super().__init__()
        self.obj_name = obj_name

    @property
    def message(self) -> str:
        if self.obj_name:
            return f"你所说的 {self.obj_name} 已经存在了"
        return "相应的对象已经存在"


class LackException(KagamiCoreException):
    """用户缺少什么的时候的报错信息"""

    def __init__(
        self, obj_type: str, required: str | float | int, current: str | float | int
    ) -> None:
        super().__init__()
        self.obj_type = obj_type
        self.required = required
        self.current = current

    @property
    def message(self) -> str:
        return (
            f"啊呀！你的 {self.obj_type} 不够了，"
            f"你需要 {self.required} {self.obj_type}，"
            f"你只有 {self.current} {self.obj_type}"
        )


class DoNotHaveException(KagamiCoreException):
    """用户没有什么东西的时候的报错"""

    def __init__(self, obj: str) -> None:
        super().__init__()
        self.obj = obj

    @property
    def message(self) -> str:
        return f"阿呀！你好像没有 {self.obj}……"


class KagamiRangeError(KagamiCoreException):
    """当用户输入的值不符合要求时抛出此异常"""

    def __init__(
        self, obj_type: str, required: str | float | int, current: str | float | int
    ) -> None:
        super().__init__()
        self.obj_type = obj_type
        self.required = required
        self.current = current

    @property
    def message(self) -> str:
        return f"这个 {self.obj_type} 的值太离谱了，一般你得要输入 {self.required}，你输入了 {self.current}"


class MultipleObjectFoundException(KagamiCoreException):
    """当用户输入的值不明确时抛出此异常"""

    def __init__(self, obj_name: str) -> None:
        super().__init__()
        self.obj_name = obj_name

    @property
    def message(self) -> str:
        return f"你说的 {self.obj_name} 对应的对象太多了，请具体一点"


class SoldOutException(KagamiCoreException):
    """当一个商品卖光时抛出的异常"""

    def __init__(self, obj_name: str) -> None:
        super().__init__()
        self.obj_name = obj_name

    @property
    def message(self) -> str:
        return f"啊哦！{self.obj_name} 卖光了！"
