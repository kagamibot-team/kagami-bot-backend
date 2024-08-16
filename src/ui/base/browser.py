"""
利用 Selenium 渲染图像
"""

from asyncio import Lock
from io import BytesIO

import PIL
import PIL.Image
from selenium.webdriver.remote.webdriver import WebDriver

from utils.threading import make_async


class BrowserRenderer:
    driver: WebDriver
    lock: Lock

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.lock = Lock()

    def _sync_render(self, link: str) -> bytes:
        # 访问相应接口
        self.driver.get(link)

        # 等待页面加载完成，包括里面的图片
        # [TODO] 求，坏枪帮忙写这里！！！
        raise NotImplementedError()

        # 截图
        return self.driver.get_screenshot_as_png()

    async def render_link(self, link: str) -> PIL.Image.Image:
        async with self.lock:
            img_data = await make_async(self._sync_render)(link)
        return PIL.Image.open(BytesIO(img_data)).convert("RGBA")
