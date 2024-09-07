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
from src.common.config import get_config


class Renderer(ABC):
    lock: Lock

    def __init__(self) -> None:
        self.lock = Lock()

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


class BrowserRenderer(Renderer):
    driver: WebDriver
    lock: Lock

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        super().__init__()

    def _sync_render(self, link: str) -> bytes:
        # 访问相应接口
        self.driver.get(link)
        logger.debug(f"WebDriver 访问了 {link}")

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

        timer2 = time.time()
        logger.debug(f"WebDriver 收到了页面加载完成的信号，耗时 {timer2 - timer}")
        timer = timer2

        time.sleep(0.3)

        # 等待图片加载完成
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script(
                "return Array.from(document.images).every(img => img.complete);"
            )
        )

        timer2 = time.time()
        logger.debug(f"WebDriver 断定图片已经加载完成了，耗时 {timer2 - timer}")
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
            result = len(self.driver.window_handles) > 0
        except WebDriverException:
            pass
        if not result:
            logger.warning("WebDriver 失效了，尝试重新启动")
            self.driver.quit()
            del self.driver
        return result


class FakeRenderer(Renderer):
    def _sync_render(self, link: str) -> bytes:
        logger.info(f"假渲染器渲染了链接：{link}")
        return Path("./res/fake-renderer-fallback.png").read_bytes()

    @property
    def available(self):
        return True


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


class RendererFactory(ABC):
    @abstractmethod
    def get(self) -> Renderer: ...


class BrowserRendererFactory(RendererFactory):
    browserFactory: BaseBrowserDriverFactory

    def __init__(self, browserFactory: BaseBrowserDriverFactory) -> None:
        self.browserFactory = browserFactory

    def get(self) -> Renderer:
        return BrowserRenderer(self.browserFactory.get())


class FakeRendererFactory(RendererFactory):
    def get(self) -> Renderer:
        return FakeRenderer()


class BrowserPool:
    renderers: list[Renderer]
    render_pointer: int = -1
    factory: RendererFactory
    count: int

    def __init__(self, factory: RendererFactory, count: int) -> None:
        self.renderers = []
        self.factory = factory
        self.count = count
        for i in range(count):
            logger.info(f"正在打开浏览器 {i+1}/{count}")
            self.renderers.append(factory.get())
            logger.info(f"打开了浏览器 {i+1}/{count}")

    async def clean_browser(self):
        """
        清理被关闭的浏览器，并重新打开
        """

        def _sync_clean():
            self.renderers = [i for i in self.renderers if i.available]
            while len(self.renderers) < self.count:
                self.renderers.append(self.factory.get())

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _sync_clean)

    @property
    def next_renderer(self) -> Renderer:
        for r in self.renderers:
            if not r.lock.locked():
                return r
        self.render_pointer += 1
        self.render_pointer %= len(self.renderers)
        return self.renderers[self.render_pointer]

    async def render(
        self, path: str, data: BaseModel | dict[str, Any] | None = None
    ) -> bytes:
        await self.clean_browser()

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

        while True:
            renderer = self.next_renderer
            try:
                return await renderer.render_link(link)
            except AssertionError as e:
                logger.exception(e)
                await self.clean_browser()


if get_config().use_fake_browser:
    factory = FakeRendererFactory()
elif get_config().browser == "chrome":
    factory = BrowserRendererFactory(ChromeFactory())
else:
    factory = BrowserRendererFactory(FirefoxFactory())
browser_pool = BrowserPool(factory, get_config().browser_count)


def get_browser_pool():
    return browser_pool
