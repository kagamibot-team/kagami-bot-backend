from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Level, LevelAltName


async def get_lid_by_name(session: AsyncSession, name: str):
    query = select(Level.data_id).filter(Level.name == name)
    res = (await session.execute(query)).scalar_one_or_none()

    if res is None:
        query = select(Level.data_id).filter(Level.alt_names.any(
            LevelAltName.name == name
        ))
        res = (await session.execute(query)).scalar_one_or_none()
    
    return res
