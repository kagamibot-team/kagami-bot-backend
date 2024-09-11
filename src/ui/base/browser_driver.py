from abc import ABC, abstractmethod

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver as Chrome
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox
from selenium.webdriver.remote.webdriver import WebDriver


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
