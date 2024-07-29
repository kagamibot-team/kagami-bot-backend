import nonebot

from src.base.event.event_timer import addInterval
from src.services.schedule import service_instance

driver = nonebot.get_driver()


async def schedule_tick():
    await service_instance.tick()


@driver.on_startup
async def _():
    addInterval(0.5, schedule_tick, skip_first=True)
