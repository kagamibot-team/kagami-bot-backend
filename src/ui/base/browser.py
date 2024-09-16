"""
利用 Selenium 渲染图像
"""

import time
from abc import abstractmethod
from pathlib import Path

import nonebot
from loguru import logger
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from src.base.exceptions import KagamiRenderWarning
from src.common.config import get_config
from src.ui.base.browser_driver import (
    BaseBrowserDriverFactory,
    ChromeFactory,
    FirefoxFactory,
)
from src.ui.base.render_worker import RenderPool, RenderWorker


class BrowserWorker(RenderWorker):
    _driver: WebDriver | None
    good = True

    @abstractmethod
    def get_factory(self) -> BaseBrowserDriverFactory: ...

    @property
    def driver(self) -> WebDriver:
        assert self._driver is not None, "WebDriver 还未初始化"
        return self._driver

    def create_driver(self) -> WebDriver:
        return self.get_factory().get()

    def __init__(self) -> None:
        self._driver = None
        super().__init__()

    def _init(self) -> None:
        self._driver = self.create_driver()

    def _ok(self) -> bool:
        result = False
        try:
            if self._driver is None:
                return False
            result = len(self.driver.window_handles) > 0
        except WebDriverException:
            pass
        return result

    def _main_render(self, link: str) -> bytes:
        # 访问相应接口
        self.driver.get(link)
        logger.debug(f"WebDriver {self.worker_id} 访问了 {link}")

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
            f"WebDriver {self.worker_id} 收到了页面加载完成的信号，耗时 {timer2 - timer}"
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
            f"WebDriver {self.worker_id} 断定图片已经加载完成了，耗时 {timer2 - timer}"
        )
        timer = timer2

        # 截图
        element = WebDriverWait(self.driver, 5).until(
            lambda d: d.find_element(By.ID, "big_box")
        )

        element_width = element.size['width']
        element_height = element.size['height']

        self.driver.set_window_size(element_width + 50, element_height + 50)

        document_width = self.driver.execute_script(
            "return document.documentElement.scrollWidth"
        )
        document_height = self.driver.execute_script(
            "return document.documentElement.scrollHeight"
        )

        # self.driver.set_window_size(document_width + 50, document_height + 50)

        logger.debug(f"Get Element Size {element_width} * {element_height}")
        logger.debug(f"Get Document Size {document_width} * {document_height}")
        logger.debug(self.driver.get_window_size())

        assert document_width < 10000, "页面宽度超过了 10000 像素，请检查页面是否过大"
        assert document_height < 10000, "页面高度超过了 10000 像素，请检查页面是否过大"

        image = element.screenshot_as_png
        timer2 = time.time()
        logger.debug(f"WebDriver 截图好了，耗时 {timer2 - timer}")

        return image

    def _render(self, link: str) -> bytes:
        try:
            return self._main_render(link)
        except (AssertionError, WebDriverException) as e:
            logger.warning(f"WebDriver 遇到了问题 {self}")
            self.good = False
            raise KagamiRenderWarning(e) from e
        except KagamiRenderWarning as e:
            self.good = False
            raise e from e

    def _quit(self) -> None:
        try:
            self.driver.quit()
            self._driver = None
            logger.info(f"WebDriver {self.worker_id} 退出")
        except WebDriverException:
            pass


class ChromeBrowserWorker(BrowserWorker):
    def get_factory(self) -> BaseBrowserDriverFactory:
        return ChromeFactory()


class FirefoxBrowserWorker(BrowserWorker):
    def get_factory(self) -> BaseBrowserDriverFactory:
        return FirefoxFactory()


class FakeRenderWorker(RenderWorker):
    def _render(self, link: str) -> bytes:
        logger.info(f"假渲染器渲染了链接：{link}")
        return Path("./res/fake-renderer-fallback.png").read_bytes()

    def _quit(self) -> None:
        pass

    def _ok(self) -> bool:
        return True

    def _init(self) -> None:
        pass


config = get_config()


port = config.render_port
if port == 0:
    port = nonebot.get_driver().config.port

if config.use_fake_browser:
    cls = FakeRenderWorker
elif config.browser == "chrome":
    cls = ChromeBrowserWorker
else:
    cls = FirefoxBrowserWorker


render_pool = RenderPool(
    cls, config.browser_count, config.render_host, port, config.render_max_fail
)


_nb_driver = nonebot.get_driver()


@_nb_driver.on_startup
async def start_up():
    await render_pool.fill()


def get_render_pool() -> RenderPool:
    return render_pool
