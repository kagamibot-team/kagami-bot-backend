"""
利用 Selenium 渲染图像
"""

import asyncio
from abc import ABC, abstractmethod
from asyncio import Lock
from pathlib import Path

import nonebot
from loguru import logger
from pydantic import BaseModel
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from src.apis.render_ui import backend_register_data
from src.common import config


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


class BrowserRenderer(Renderer):
    driver: WebDriver
    lock: Lock

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        super().__init__()

    def _sync_render(self, link: str) -> bytes:
        # 访问相应接口
        self.driver.get(link)

        # 等待页面加载完成
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState;")
            == "complete"
        )

        # 等待前端返回相关信号
        WebDriverWait(self.driver, 20).until(
            lambda driver: driver.execute_script(
                "return window.loaded_trigger_signal !== undefined;"
            )
        )

        # 等待图片加载完成
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script(
                "return Array.from(document.images).every(img => img.complete);"
            )
        )

        # 截图
        element = WebDriverWait(self.driver, 5).until(
            lambda d: d.find_element(By.ID, "big_box")
        )
        element_width: float = element.size["width"]
        element_height: float = element.size["height"]
        self.driver.set_window_size(element_width + 50, element_height + 50)
        return element.screenshot_as_png


class FakeRenderer(Renderer):
    def _sync_render(self, link: str) -> bytes:
        logger.info(f"假渲染器渲染了链接：{link}")
        return Path("./res/fake-renderer-fallback.png").read_bytes()


class BrowserDriverFactory(ABC):
    @abstractmethod
    def get(self) -> WebDriver: ...


class ChromeFactory(BrowserDriverFactory):
    def get(self) -> WebDriver:
        opt = ChromeOptions()
        opt.add_argument("--headless")
        opt.add_argument("--enable-webgl")
        opt.add_argument("--allow-file-access-from-files")
        driver = Chrome(options=opt)
        return driver


class RendererFactory(ABC):
    @abstractmethod
    def get(self) -> Renderer: ...


class BrowserRendererFactory(RendererFactory):
    browserFactory: BrowserDriverFactory

    def __init__(self, browserFactory: BrowserDriverFactory) -> None:
        self.browserFactory = browserFactory

    def get(self) -> Renderer:
        return BrowserRenderer(self.browserFactory.get())


class FakeRendererFactory(RendererFactory):
    def get(self) -> Renderer:
        return FakeRenderer()


class BrowserPool:
    renderers: list[Renderer]
    render_pointer: int = -1

    def __init__(self, rendererFactory: RendererFactory, count: int) -> None:
        self.renderers = []
        for i in range(count):
            self.renderers.append(rendererFactory.get())
            logger.info(f"打开了浏览器 {i+1}/{count}")

    async def render(self, path: str, data: BaseModel | None = None) -> bytes:
        query = ""
        if data is not None:
            uuid = backend_register_data(data)
            query = f"?uuid={uuid}"
        nbdriver = nonebot.get_driver()
        port = nbdriver.config.port
        link = f"http://127.0.0.1:{port}/kagami/pages/{path}{query}"
        for r in self.renderers:
            if not r.lock.locked():
                return await r.render_link(link)
        self.render_pointer += 1
        self.render_pointer %= len(self.renderers)
        return await self.renderers[self.render_pointer].render_link(link)


if config.config.use_fake_browser:
    factory = FakeRendererFactory()
else:
    factory = BrowserRendererFactory(ChromeFactory())
browser_pool = BrowserPool(factory, config.config.browser_count)


def get_browser_pool():
    return browser_pool
