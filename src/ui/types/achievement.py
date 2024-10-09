from pydantic import BaseModel, computed_field

from src.core.unit_of_work import UnitOfWork
from src.services.achievements.base import Achievement, DisplayRule


class AchievementDisplay(BaseModel):
    meta: Achievement
    achieved: bool

    @property
    def should_display(self):
        return not (
            self.meta.display_rule == DisplayRule.hide_until_achieve
            and not self.achieved
        )

    @staticmethod
    async def get(
        uow: UnitOfWork, achievement: Achievement, uid: int | None
    ) -> "AchievementDisplay":
        if uid is None:
            return AchievementDisplay(
                meta=achievement,
                achieved=True,
            )

        return AchievementDisplay(
            meta=achievement, achieved=await achievement.have_got(uow, uid)
        )
