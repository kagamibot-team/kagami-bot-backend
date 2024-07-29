from src.base.schedule import Schedule
from src.common.times import now_datetime


class ScheduleService:
    schedules: list[Schedule]

    def __init__(self) -> None:
        self.schedules = []

    async def tick(self):
        time = now_datetime()
        for schedule in self.schedules:
            if schedule.should_do(time):
                await schedule.do()


service_instance = ScheduleService()
