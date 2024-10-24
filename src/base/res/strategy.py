from abc import ABC, abstractmethod
from hashlib import sha256
from pathlib import Path
import tempfile

from loguru import logger

from src.base.res.middleware.filter import ITextFilter
from src.base.res.middleware.image import BaseImageMiddleware
from src.base.res.resource import IResource, LocalResource
from src.ui.base.tools import image_to_bytes


class IStorageStrategy(ABC):
    @abstractmethod
    def exists(self, file_name: str) -> bool:
        """检查文件是否存在"""

    @abstractmethod
    def get(self, file_name: str) -> IResource:
        """获取文件内容"""

    @abstractmethod
    def can_put(self, file_name: str) -> bool:
        """检查是否可以写入文件"""

    @abstractmethod
    def put(self, file_name: str, data: bytes) -> IResource:
        """上传文件内容"""

    def __call__(self, file_name: str) -> IResource:
        if not self.exists(file_name):
            raise FileNotFoundError(f"File {file_name} not found")
        return self.get(file_name)


class IWriteableStorageStrategy(IStorageStrategy):
    def can_put(self, file_name: str) -> bool:
        """检查是否可以写入文件"""
        return True


class IReadonlyStorageStrategy(IStorageStrategy):
    def put(self, file_name: str, data: bytes) -> IResource:
        raise NotImplementedError("Readonly storage strategy can't put data")

    def can_put(self, file_name: str) -> bool:
        return False


class StaticStorageStrategy(IReadonlyStorageStrategy):
    """
    嵌入代码库的资源文件储存方案
    """

    def __init__(self, root: Path = Path("./res")):
        self.root = root

    def exists(self, file_name: str) -> bool:
        return (self.root / file_name).exists()

    def get(self, file_name: str) -> IResource:
        return LocalResource(self.root / file_name)


class FileStorageStrategy(IWriteableStorageStrategy):
    """
    文件系统储存方案
    """

    def __init__(self, root: Path = Path("./data")):
        self.root = root

    def exists(self, file_name: str) -> bool:
        return (self.root / file_name).exists()

    def get(self, file_name: str) -> IResource:
        return LocalResource(self.root / file_name)

    def put(self, file_name: str, data: bytes) -> IResource:
        # 先确保文件夹存在
        self.root.mkdir(parents=True, exist_ok=True)
        self.root.joinpath(file_name).write_bytes(data)
        return self.get(file_name)


class TempdirStorageStrategy(IWriteableStorageStrategy):
    """
    临时文件夹储存方案
    """

    tempdir: tempfile.TemporaryDirectory[str] | None = None

    def __init__(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def exists(self, file_name: str) -> bool:
        return (self.root / file_name).exists()

    def get(self, file_name: str) -> IResource:
        return LocalResource(self.root / file_name)

    def put(self, file_name: str, data: bytes) -> IResource:
        self.root.joinpath(file_name).write_bytes(data)
        return self.get(file_name)

    # 需要管理声明周期。当程序退出时，需要清理临时文件夹
    def __del__(self):
        if self.tempdir is not None:
            self.tempdir.cleanup()
            self.tempdir = None


class ShadowStorageStrategy(IReadonlyStorageStrategy):
    """
    阴影储存方案。方案是从主储存方案中，获取图片，经过中间件处理以后，再储存
    到一个临时储存方案中。中间件使用 PILLOW 处理图片。
    """

    def __init__(
        self,
        main: IStorageStrategy,
        shadow: IStorageStrategy,
        task_chain: list[BaseImageMiddleware] | BaseImageMiddleware | None = None,
        suffix: str = ".png",
    ):
        self.main = main
        self.shadow = shadow
        if isinstance(task_chain, BaseImageMiddleware):
            task_chain = [task_chain]
        self.task_chain = task_chain or []
        self.suffix = suffix

    def exists(self, file_name: str) -> bool:
        return self.main.exists(file_name)

    def get_output_file_name(self, res: IResource) -> str:
        # 先读取原图像，sha256 后添加后缀
        data = res.path.read_bytes()
        data += self.suffix.encode()
        for task in self.task_chain:
            data += task.to_string().encode()
        return sha256(data).hexdigest() + self.suffix

    def get(self, file_name: str) -> IResource:
        image = self.main.get(file_name)
        if self.shadow.exists(self.get_output_file_name(image)):
            # 如果图像存在，就不重复处理了
            return self.shadow.get(self.get_output_file_name(image))
        image_obj = image.load_pil_image()
        logger.debug(
            f"Processing image {file_name} with {len(self.task_chain)} middlewares"
        )
        for task in self.task_chain:
            image_obj = task.handle(image_obj)
        return self.shadow.put(
            self.get_output_file_name(image),
            image_to_bytes(image_obj, suffix=self.suffix),
        )


class JustFallBackStorageStrategy(IReadonlyStorageStrategy):
    """
    不管怎么样，直接回退到同一个文件
    """

    def __init__(self, fp: Path = Path("./res/小镜指.jpg")):
        self.fp = fp

    def exists(self, file_name: str) -> bool:
        return self.fp.exists()

    def get(self, file_name: str) -> IResource:
        return LocalResource(self.fp)


class FilteredStorageStrategy(IStorageStrategy):
    """
    过滤储存方案。根据文件名过滤，只允许特定文件名通过
    """

    filters: list[ITextFilter]

    def __init__(
        self,
        strategy: IStorageStrategy,
        filters: list[ITextFilter] | ITextFilter | None,
    ):
        self.strategy = strategy
        if isinstance(filters, ITextFilter):
            filters = [filters]
        if filters is None:
            filters = []
        self.filters = filters

    def exists(self, file_name: str) -> bool:
        return self.strategy.exists(file_name) and all(
            [filter.match(file_name) for filter in self.filters]
        )

    def get(self, file_name: str) -> IResource:
        return self.strategy.get(file_name)

    def can_put(self, file_name: str) -> bool:
        return all(
            [filter.match(file_name) for filter in self.filters]
        ) and self.strategy.can_put(file_name)

    def put(self, file_name: str, data: bytes) -> IResource:
        return self.strategy.put(file_name, data)


class CombinedStorageStrategy(IStorageStrategy):
    """
    将多个储存方案组合起来
    """

    def __init__(self, strategies: list[IStorageStrategy]):
        self.strategies = strategies

    def exists(self, file_name: str) -> bool:
        return any([strategy.exists(file_name) for strategy in self.strategies])

    def get(self, file_name: str) -> IResource:
        for strategy in self.strategies:
            if strategy.exists(file_name):
                return strategy.get(file_name)
        raise FileNotFoundError(file_name)

    def put(self, file_name: str, data: bytes) -> IResource:
        for strategy in self.strategies:
            if strategy.can_put(file_name):
                continue
            return strategy.put(file_name, data)
        raise ValueError("No writable strategy")

    def can_put(self, file_name: str) -> bool:
        return any([strategy.can_put(file_name) for strategy in self.strategies])
