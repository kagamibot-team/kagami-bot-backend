class KagamiCoreException(Exception):
    """小镜 Bot 抓小哥游戏的错误类型的基类"""

    @property
    def message(self) -> str:
        return "通常来说，你应该看不到这条错误信息。如果你看到了，请联系开发组修复。"

    def __str__(self) -> str:
        return self.message


class KagamiStopIteration(KagamiCoreException):
    """小镜 Bot 停止处理消息的错误类型"""


class ObjectNotFoundException(KagamiCoreException):
    """当找不到某个对象时抛出此异常"""

    def __init__(self, obj_type: str | None = None) -> None:
        super().__init__()
        self.obj_type = obj_type

    @property
    def message(self) -> str:
        msg = f"抱歉！档案中没有这个{self.obj_type}，请检查输入是否有误！"
        return msg


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
        return f"阿呀！你好像没有「{self.obj}」……"


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


class NoAwardException(KagamiCoreException):
    """当前猎场没有小哥时抛出的异常"""

    @property
    def message(self) -> str:
        return "现在的猎场没有小哥哦！去其他猎场看看吧！"


class PackNotMatchException(KagamiCoreException):
    """当前的猎场并不是需要的猎场时的报错"""

    def __init__(self, current: int, required: int) -> None:
        super().__init__()
        self.current = current
        self.required = required

    @property
    def message(self) -> str:
        return f"你现在并不在 {self.required} 猎场，你现在在 {self.current} 猎场"


class SleepToLateException(KagamiCoreException):
    """想睡太晚的时候的报错"""

    @property
    def message(self):
        return "真能睡懒觉，要不早点起来吧"


class SleepToEarlyException(KagamiCoreException):
    """想睡太早的时候的报错"""

    @property
    def message(self):
        return "嗯？你这也太早起了吧？"


class NotSleepTimeException(KagamiCoreException):
    """不是睡觉时间的报错"""

    @property
    def message(self):
        return "诶，现在不是睡觉的时候吧……"


class UnknownArgException(KagamiCoreException):
    """不知道一个参数的意思"""

    def __init__(self, arg: str) -> None:
        self.arg = arg

    @property
    def message(self):
        return f"我好像没搞懂你说 {self.arg} 是什么意思……"


class KagamiRenderWarning(KagamiCoreException):
    """
    渲染图片时的问题，但此时不是核心报错
    """

    def __init__(self, exc: Exception) -> None:
        super().__init__()
        self.exception = exc


class KagamiRenderException(KagamiCoreException):
    """渲染图片的时候的报错"""

    def __init__(self, work_id: str) -> None:
        super().__init__()
        self.work_id = work_id

    @property
    def message(self) -> str:
        return (
            f"渲染图片的时候出了点问题！请联系 PT 修复呀！报错的渲染器：{self.work_id}"
        )


class KagamiArgumentException(KagamiCoreException):
    """其他参数有误时的报错"""

    def __init__(self, arg: str) -> None:
        super().__init__()
        self.arg = arg

    @property
    def message(self) -> str:
        return f"{self.arg}"
