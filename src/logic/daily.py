from random import Random

from sqlalchemy import select

from src.common.times import now_datetime
from src.core.unit_of_work import UnitOfWork
from src.models.models import Award

CACHED_DAILY: dict[str, int] = {}


async def get_daily(uow: UnitOfWork, random: Random | None = None):
    """获得每日小哥"""

    key = str(now_datetime().date())
    if key in CACHED_DAILY:
        return CACHED_DAILY[key]

    if random is None:
        random = Random(key)

    level = random.choices(uow.levels.sorted, [l.weight for l in uow.levels.sorted])[0]
    query = select(Award.data_id).filter(
        Award.level_id == level.lid, Award.is_special_get_only.is_not(True)
    )
    awards = (await uow.session.execute(query)).tuples().all()
    aid = random.choice(awards)[0]
    CACHED_DAILY[key] = aid

    return aid
