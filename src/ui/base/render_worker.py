import asyncio
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Generic, TypeVar

from loguru import logger
from pydantic import BaseModel

from src.apis.render_ui import backend_register_data
from src.base.exceptions import KagamiRenderException, KagamiRenderWarning

TEMP = {"work_id": 0}


def get_next_work_id() -> str:
    TEMP["work_id"] += 1
    return "#" + str(TEMP["work_id"])


class RenderWorker(ABC):
    """
    # RenderWorker

    `RenderWorker` 是渲染器的基类。渲染器用于将网页渲染为图片。

    ## 需要继承

    ### `_render` 方法

    渲染的核心逻辑，以及一些错误处理。
    如果是可以被挽回的渲染错误，请在捕捉到错误后将错误包装为
    `KagamiRenderWarning` 并重新抛出。例如：

    ```python
    try:
        ...
    except WebDriverException as e:
        raise KagamiRenderWarning(e)
    ```

    ### `_ok` 方法

    用于获取当前工作者的状态。True 代表当前工作正常

    ### `_init` 方法

    用于初始化当前工作者，例如，启动一个新的浏览器。

    ### `_quit` 方法

    尝试退出当前会话，例如，关闭浏览器等。该方法应该尽可能避免抛出错误。
    例如，浏览器已经关闭时，不应该抛出错误，而是跳过关闭流程。
    """

    worker_id: str
    last_render_begin: float
    started: bool
    exited: bool

    def __init__(self) -> None:
        self.worker_id = get_next_work_id()
        self.last_render_begin = 0
        self.started = False
        self.exited = False

    @abstractmethod
    def _render(self, link: str) -> bytes: ...

    def render(self, link: str) -> bytes:
        self.last_render_begin = time.time()
        logger.info(f"渲染器开始渲染 Worker={self} Link={link}")
        result = self._render(link)
        logger.info(f"渲染器渲染结束 Worker={self} Link={link}")
        return result

    @abstractmethod
    def _ok(self) -> bool: ...

    @property
    def ok(self) -> bool:
        return (self._ok() or not self.started) and not self.exited

    @abstractmethod
    def _init(self): ...

    def init(self) -> None:
        try:
            logger.info(f"渲染器开始启动 Worker={self}")
            self._init()
            logger.info(f"渲染器启动成功 Worker={self}")
        finally:
            self.started = True

    @abstractmethod
    def _quit(self): ...

    def quit(self) -> None:
        if self.exited:
            logger.warning(
                "渲染器已经是正在退出的状态了，但是退出方法被重复调用。"
                f"此时仍然会尝试退出 Worker={self}"
            )
        else:
            logger.info(f"渲染器正在退出 Worker={self}")
        self._quit()
        self.exited = True
        logger.info(f"渲染器退出了 Worker={self}")

    def __str__(self) -> str:
        return f"[{self.__class__.__name__} {self.worker_id}]"

    def __del__(self) -> None:
        if not self.exited:
            logger.warning(f"是不是忘记回收渲染器了？没关系，我帮你关！ Worker={self}")
            self.quit()


T = TypeVar("T", bound=RenderWorker)


class RenderPool(Generic[T]):
    """
    渲染器池
    """

    executor: ThreadPoolExecutor

    starting: set[RenderWorker]
    working: set[RenderWorker]
    worker_pool: asyncio.Queue[RenderWorker]
    cls: type[T]
    count: int
    host: str
    port: int
    max_fail: int

    def __init__(
        self, cls: type[T], count: int, host: str, port: int, max_fail: int
    ) -> None:
        self.executor = ThreadPoolExecutor()
        self.worker_pool = asyncio.Queue()
        self.cls = cls
        self.count = count
        self.host = host
        self.port = port
        self.max_fail = max_fail

        self.working = set()
        self.starting = set()

    async def put(self, cls: type[RenderWorker] | None = None) -> None:
        if cls is None:
            cls = self.cls
        asyncio.create_task(self._worker_initializer(cls))

    async def _worker_initializer(self, cls: type[RenderWorker] | None = None) -> None:
        if cls is None:
            cls = self.cls
        loop = asyncio.get_event_loop()
        worker = cls()
        self.starting.add(worker)
        await loop.run_in_executor(self.executor, worker.init)
        self.starting.remove(worker)
        await self.worker_pool.put(worker)

    async def _worker_quit(self, worker: RenderWorker) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, worker.quit)

    async def worker_render(self, worker: RenderWorker, link: str) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, worker.render, link)

    async def leave(self, worker: RenderWorker) -> None:
        asyncio.create_task(self._worker_quit(worker))

    async def fill(self) -> None:
        """
        装载 Worker，如果数量超了，则不管
        """
        for _ in range(self.count):
            await self.put()

    async def clean(self) -> None:
        """
        清理异常的渲染器，并重新打开
        """

        tmp: list[RenderWorker] = []
        while not self.worker_pool.empty():
            # 将所有 worker 临时取出
            worker = await self.worker_pool.get()
            tmp.append(worker)

        for worker in tmp:
            if not worker.ok:
                logger.warning(f"有渲染器工作不正常 Worker={worker}")
                if not worker.exited:
                    await self.leave(worker)
                await self.put()
            else:
                # 将正常的渲染器放回
                await self.worker_pool.put(worker)

    async def reload(self, worker_id: str | None = None) -> None:
        """
        关闭渲染器并重载
        """

        tmp: list[RenderWorker] = []
        while not self.worker_pool.empty():
            worker = await self.worker_pool.get()
            tmp.append(worker)

        if worker_id is None:
            logger.info("渲染器 RELOAD 调用，将关闭所有渲染器")
            for worker in tmp:
                await self._worker_quit(worker)
                await self.put()
            for worker in self.working:
                await self._worker_quit(worker)
                await self.put()
            self.working.clear()
        else:
            logger.info(f"渲染器 RELOAD 调用，将关闭指定渲染器 ID={worker_id}")
            for worker in tmp:
                if worker.worker_id != worker_id:
                    await self.worker_pool.put(worker)
                else:
                    await self._worker_quit(worker)
                    await self.put()
                    return
            for worker in self.working:
                if worker.worker_id == worker_id:
                    await self._worker_quit(worker)
                    await self.put()
                    self.working.remove(worker)
                    return

    async def kill(self, worker_id: str):
        """
        关闭渲染器并重载
        """

        tmp: list[RenderWorker] = []
        while not self.worker_pool.empty():
            worker = await self.worker_pool.get()
            tmp.append(worker)

        logger.info(f"渲染器 KILL 调用，将关闭指定渲染器 ID={worker_id}")
        for worker in tmp:
            if worker.worker_id != worker_id:
                await self.worker_pool.put(worker)
            else:
                await self._worker_quit(worker)
                return
        for worker in self.working:
            if worker.worker_id == worker_id:
                await self._worker_quit(worker)
                self.working.remove(worker)
                return

    async def render(
        self, path: str, data: BaseModel | dict[str, Any] | None = None
    ) -> bytes:
        await self.clean()

        query = ""
        if data is not None:
            uuid = backend_register_data(data)
            query = f"?uuid={uuid}"
            logger.debug(f"已经将数据暂存到 {uuid} 了")
        link = f"http://{self.host}:{self.port}/kagami/pages/{path}{query}"

        fail = 0
        while True:
            worker = await self.worker_pool.get()
            self.working.add(worker)
            try:
                img = await self.worker_render(worker, link)
                await self.worker_pool.put(worker)
                return img
            except KagamiRenderWarning as e:
                logger.warning(
                    f"渲染器渲染失败 Worker={worker} Exception={e.exception}"
                )
                logger.exception(e.exception)
                fail += 1
                # 推入一个新的 Worker，保证数量不减少
                await self.put()
                await self.leave(worker)
            finally:
                self.working.remove(worker)

            if fail > self.max_fail and self.max_fail > 0:
                raise KagamiRenderException(worker.worker_id)

    async def get_worker_list(
        self,
    ) -> tuple[list[RenderWorker], list[RenderWorker], list[RenderWorker]]:
        # 傻方法之：全部拿出来
        idle: list[RenderWorker] = []
        while not self.worker_pool.empty():
            worker = await self.worker_pool.get()
            idle.append(worker)
        for worker in idle:
            await self.worker_pool.put(worker)

        return idle, list(self.working), list(self.starting)
