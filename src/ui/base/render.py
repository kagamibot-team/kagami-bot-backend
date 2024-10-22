"""
利用 Selenium 渲染图像
"""

from typing import Any
import nonebot
from src.common.config import get_config
from src.ui.base.browser_worker import (
    ChromeBrowserWorker,
    FakeRenderWorker,
    FirefoxBrowserWorker,
)
from src.ui.base.rabbitmq_worker import RabbitMQWorker
from src.ui.base.render_worker import RenderPool


config = get_config()


port = config.render_port
if port == 0:
    port = nonebot.get_driver().config.port

if config.use_fake_browser:
    cls = FakeRenderWorker
elif config.renderer == "service":
    cls = lambda: RabbitMQWorker(
        config.rabbitmq_host,
        config.rabbitmq_port,
        config.rabbitmq_virtual_host,
        config.rabbitmq_account,
        config.rabbitmq_password,
    )
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


def get_render_pool() -> RenderPool[Any]:
    return render_pool
