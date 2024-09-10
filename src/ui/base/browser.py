"""
利用 Selenium 渲染图像
"""

import asyncio
import time
from abc import ABC, abstractmethod
from asyncio import Lock
from pathlib import Path
from typing import Any

import nonebot
from loguru import logger
from pydantic import BaseModel
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from src.apis.render_ui import backend_register_data
from src.base.exceptions import KagamiCoreException, KagamiRenderException
from src.common.config import get_config

TEMP = {"work_id": 0}


def get_next_work_id() -> str:
    TEMP["work_id"] += 1
    return "#" + str(TEMP["work_id"])


class RenderWorker(ABC):
    lock: Lock
    work_id: str

    def __init__(self) -> None:
        self.lock = Lock()
        self.work_id = get_next_work_id()

    @abstractmethod
    def _sync_render(self, link: str) -> bytes: ...

    async def render_link(self, link: str) -> bytes:
        async with self.lock:
            loop = asyncio.get_event_loop()

            def _render():
                return self._sync_render(link)

            img_data = await loop.run_in_executor(None, _render)
        return img_data

    @property
    @abstractmethod
    def available(self) -> bool: ...

    @abstractmethod
    def quit(self) -> None: ...

    def __str__(self) -> str:
        return f"[{self.__class__.__name__} {self.work_id}]"


class BrowserWorker(RenderWorker):
    _driver: WebDriver | None
    lock: Lock

    @property
    def driver(self) -> WebDriver:
        assert self._driver is not None, "WebDriver 还未初始化"
        return self._driver

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        super().__init__()

    def _sync_render(self, link: str) -> bytes:
        # 访问相应接口
        self.driver.get(link)
        logger.debug(f"WebDriver {self.work_id} 访问了 {link}")

        timer = time.time()

        # 等待页面加载完成
        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.execute_script("return document.readyState;")
            == "complete"
        )

        # 等待前端返回相关信号
        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.execute_script(
                "return window.loaded_trigger_signal !== undefined;"
            )
        )

        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.execute_script(
                "return window.loaded_data_signal !== false;"
            )
        )

        timer2 = time.time()
        logger.debug(
            f"WebDriver {self.work_id} 收到了页面加载完成的信号，耗时 {timer2 - timer}"
        )
        timer = timer2

        time.sleep(0.3)

        # 等待图片加载完成
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script(
                "return Array.from(document.images).every(img => img.complete);"
            )
        )

        timer2 = time.time()
        logger.debug(
            f"WebDriver {self.work_id} 断定图片已经加载完成了，耗时 {timer2 - timer}"
        )
        timer = timer2

        # 截图
        element = WebDriverWait(self.driver, 5).until(
            lambda d: d.find_element(By.ID, "big_box")
        )

        document_width = self.driver.execute_script(
            "return document.documentElement.scrollWidth"
        )
        document_height = self.driver.execute_script(
            "return document.documentElement.scrollHeight"
        )

        self.driver.set_window_size(document_width + 500, document_height + 500)

        logger.debug(f"Get Document Size {document_width} * {document_height}")
        logger.debug(self.driver.get_window_size())

        assert document_width < 10000, "页面宽度超过了 10000 像素，请检查页面是否过大"
        assert document_height < 10000, "页面高度超过了 10000 像素，请检查页面是否过大"

        image = element.screenshot_as_png
        timer2 = time.time()
        logger.debug(f"WebDriver 截图好了，耗时 {timer2 - timer}")

        return image

    @property
    def available(self):
        result = False
        try:
            if self._driver is None:
                return False
            result = len(self.driver.window_handles) > 0
        except WebDriverException:
            pass
        if not result:
            logger.warning(f"WebDriver {self.work_id} 失效了")
            self.quit()
        return result

    def quit(self) -> None:
        self.driver.quit()
        self._driver = None
        logger.info(f"WebDriver {self.work_id} 退出")


class FakeRenderWorker(RenderWorker):
    def _sync_render(self, link: str) -> bytes:
        logger.info(f"假渲染器渲染了链接：{link}")
        return Path("./res/fake-renderer-fallback.png").read_bytes()

    @property
    def available(self):
        return True

    def quit(self) -> None:
        pass


class BaseBrowserDriverFactory(ABC):
    @abstractmethod
    def get(self) -> WebDriver: ...


class ChromeFactory(BaseBrowserDriverFactory):
    def get(self) -> WebDriver:
        opt = ChromeOptions()
        opt.add_argument("--headless")
        opt.add_argument("--enable-webgl")
        opt.add_argument("--allow-file-access-from-files")

        # 对 Docker 环境的支持
        opt.add_argument("--disable-dev-shm-usage")
        # 容器内存共享的空间较小，导致 Chrome 无法正常启动。

        opt.add_argument("--no-sandbox")
        # 在 Docker 中运行 Chrome 时，--no-sandbox 是必需的，
        # 因为默认的沙箱模式在容器中无法正确工作。

        # 其他的一些选项
        opt.add_argument("--disable-gpu")
        opt.add_argument("--disable-extensions")
        opt.add_argument("--disable-infobars")
        opt.add_argument("--start-maximized")
        opt.add_argument("--disable-notifications")

        # 对 Docker 环境的支持
        opt.add_argument("--disable-dev-shm-usage")
        # 容器内存共享的空间较小，导致 Chrome 无法正常启动。

        opt.add_argument("--no-sandbox")
        # 在 Docker 中运行 Chrome 时，--no-sandbox 是必需的，
        # 因为默认的沙箱模式在容器中无法正确工作。

        # 其他的一些选项
        opt.add_argument("--disable-gpu")
        opt.add_argument("--disable-extensions")
        opt.add_argument("--disable-infobars")
        opt.add_argument("--start-maximized")
        opt.add_argument("--disable-notifications")

        driver = Chrome(options=opt)
        return driver


class FirefoxFactory(BaseBrowserDriverFactory):
    def get(self) -> WebDriver:
        opt = FirefoxOptions()
        opt.add_argument("-headless")

        # 对 Docker 环境的支持
        opt.add_argument("--disable-dev-shm-usage")
        opt.add_argument("--no-sandbox")

        # 其他的一些选项
        opt.add_argument("--disable-gpu")
        opt.add_argument("--start-maximized")
        opt.add_argument("--disable-notifications")

        # 启用 WebGL 和允许文件访问
        opt.set_preference("webgl.disabled", False)
        opt.set_preference("dom.file.createInChild", True)

        # 创建 WebDriver 实例
        driver = Firefox(options=opt)
        return driver


class RenderWorkerFactory(ABC):
    @abstractmethod
    def get(self) -> RenderWorker: ...


class BrowserWorkerFactory(RenderWorkerFactory):
    browserFactory: BaseBrowserDriverFactory

    def __init__(self, browserFactory: BaseBrowserDriverFactory) -> None:
        self.browserFactory = browserFactory

    def get(self) -> RenderWorker:
        return BrowserWorker(self.browserFactory.get())


class FakeWorkerFactory(RenderWorkerFactory):
    def get(self) -> RenderWorker:
        return FakeRenderWorker()


class BrowserPool:
    workers: list[RenderWorker]
    last_render_task: int = -1
    factory: RenderWorkerFactory
    count: int

    def __init__(self, factory: RenderWorkerFactory, count: int) -> None:
        self.workers = []
        self.factory = factory
        self.count = count
        for i in range(count):
            logger.info(f"正在打开浏览器 {i+1}/{count}")
            self.workers.append(factory.get())
            logger.info(f"打开了浏览器 {i+1}/{count}")

    async def clean(self):
        """
        清理被关闭的浏览器，并重新打开
        """

        def _sync_clean():
            self.workers = [i for i in self.workers if i.available]
            while len(self.workers) < self.count:
                self.workers.append(self.factory.get())

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _sync_clean)

    async def reload(self, work_id: str | None = None):
        if work_id is None:
            for worker in self.workers:
                worker.quit()
        else:
            for i in self.workers:
                if i.work_id == work_id:
                    i.quit()
                    break

        await self.clean()

    @property
    def next_worker(self) -> RenderWorker:
        for r in self.workers:
            if not r.lock.locked():
                return r
        self.last_render_task += 1
        self.last_render_task %= len(self.workers)
        return self.workers[self.last_render_task]

    async def render(
        self, path: str, data: BaseModel | dict[str, Any] | None = None
    ) -> bytes:
        await self.clean()

        query = ""
        if data is not None:
            uuid = backend_register_data(data)
            query = f"?uuid={uuid}"
            logger.debug(f"已经将数据暂存到 {uuid} 了")

        nbdriver = nonebot.get_driver()
        port: int = nbdriver.config.port
        if (_port := get_config().render_port) != 0:
            port = int(_port)

        link = f"http://{get_config().render_host}:{port}/kagami/pages/{path}{query}"

        logger.debug(f"访问 {link} 进行渲染")

        failed_count = 0

        while True:
            worker = self.next_worker
            logger.info(f"呼叫 {worker}")
            try:
                return await worker.render_link(link)
            except AssertionError:
                worker.quit()
                await self.clean()
            except WebDriverException as e:
                logger.info(f"{worker} 渲染失败了")
                logger.exception(e)
                failed_count += 1
                if failed_count >= 3:
                    raise KagamiRenderException(worker.work_id)


if get_config().use_fake_browser:
    factory = FakeWorkerFactory()
elif get_config().browser == "chrome":
    factory = BrowserWorkerFactory(ChromeFactory())
else:
    factory = BrowserWorkerFactory(FirefoxFactory())
browser_pool = BrowserPool(factory, get_config().browser_count)


def get_browser_pool():
    return browser_pool
