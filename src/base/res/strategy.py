from abc import ABC, abstractmethod
from hashlib import sha256
from pathlib import Path

import aiofiles

from src.base.res.middleware.filter import ITextFilter
from src.base.res.middleware.image import BaseImageMiddleware
from src.base.res.resource import IResource, LocalResource
from src.common.threading import make_async
from src.ui.base.tools import image_to_bytes


class IStorageStrategy(ABC):
    @abstractmethod
    async def exists(self, file_name: str) -> bool:
        """检查文件是否存在"""

    @abstractmethod
    async def get(self, file_name: str) -> IResource:
        """获取文件内容"""

    @abstractmethod
    async def can_put(self, file_name: str) -> bool:
        """检查是否可以写入文件"""

    @abstractmethod
    async def put(self, file_name: str, data: bytes) -> IResource:
        """上传文件内容"""


class IWriteableStorageStrategy(IStorageStrategy):
    async def can_put(self, file_name: str) -> bool:
        """检查是否可以写入文件"""
        return True


class IReadonlyStorageStrategy(IStorageStrategy):
    async def put(self, file_name: str, data: bytes) -> IResource:
        raise NotImplementedError("Readonly storage strategy can't put data")

    async def can_put(self, file_name: str) -> bool:
        return False


class StaticStorageStrategy(IReadonlyStorageStrategy):
    """
    嵌入代码库的资源文件储存方案
    """

    def __init__(self, root: Path = Path("./res")):
        self.root = root

    async def exists(self, file_name: str) -> bool:
        return (self.root / file_name).exists()

    async def get(self, file_name: str) -> IResource:
        return LocalResource(self.root / file_name)


class FileStorageStrategy(IWriteableStorageStrategy):
    """
    文件系统储存方案
    """

    def __init__(self, root: Path = Path("./data")):
        self.root = root

    async def exists(self, file_name: str) -> bool:
        return (self.root / file_name).exists()

    async def get(self, file_name: str) -> IResource:
        return LocalResource(self.root / file_name)

    async def put(self, file_name: str, data: bytes) -> IResource:
        # 先确保文件夹存在
        self.root.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.root / file_name, "wb") as f:
            await f.write(data)
        return await self.get(file_name)


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

    async def exists(self, file_name: str) -> bool:
        return await self.main.exists(file_name)

    def get_output_file_name(self, res: IResource) -> str:
        # 先读取原图像，sha256 后添加后缀
        data = res.path.read_bytes()
        return sha256(data).hexdigest() + self.suffix

    async def get(self, file_name: str) -> IResource:
        image = await self.main.get(file_name)
        if self.shadow.exists(self.get_output_file_name(image)):
            # 如果图像存在，就不重复处理了
            return await self.shadow.get(self.get_output_file_name(image))
        image_obj = image.load_pil_image()
        for task in self.task_chain:
            image_obj = await task.handle(image_obj)
        return await self.shadow.put(
            self.get_output_file_name(image),
            await make_async(image_to_bytes)(image_obj, suffix=self.suffix),
        )


class JustFallBackStorageStrategy(IReadonlyStorageStrategy):
    """
    不管怎么样，直接回退到同一个文件
    """

    def __init__(self, fp: Path = Path("./res/小镜指.jpg")):
        self.fp = fp

    async def exists(self, file_name: str) -> bool:
        return self.fp.exists()

    async def get(self, file_name: str) -> IResource:
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

    async def exists(self, file_name: str) -> bool:
        return await self.strategy.exists(file_name) and all(
            [await filter.match(file_name) for filter in self.filters]
        )

    async def get(self, file_name: str) -> IResource:
        return await self.strategy.get(file_name)

    async def can_put(self, file_name: str) -> bool:
        return all(
            [await filter.match(file_name) for filter in self.filters]
        ) and await self.strategy.can_put(file_name)

    async def put(self, file_name: str, data: bytes) -> IResource:
        return await self.strategy.put(file_name, data)


class CombinedStorageStrategy(IStorageStrategy):
    """
    将多个储存方案组合起来
    """

    def __init__(self, strategies: list[IStorageStrategy]):
        self.strategies = strategies

    async def exists(self, file_name: str) -> bool:
        return any([await strategy.exists(file_name) for strategy in self.strategies])

    async def get(self, file_name: str) -> IResource:
        for strategy in self.strategies:
            if await strategy.exists(file_name):
                return await strategy.get(file_name)
        raise FileNotFoundError(file_name)

    async def put(self, file_name: str, data: bytes) -> IResource:
        for strategy in self.strategies:
            if await strategy.can_put(file_name):
                continue
            return await strategy.put(file_name, data)
        raise ValueError("No writable strategy")

    async def can_put(self, file_name: str) -> bool:
        return any([await strategy.can_put(file_name) for strategy in self.strategies])
