from typing import cast
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import *


async def get_or_create_tag(session: AsyncSession, tag_name: str, tag_args: str) -> int:
    query = select(Tag.data_id).filter(
        Tag.tag_name == tag_name, Tag.tag_args == tag_args
    )
    tag = (await session.execute(query)).scalar_one_or_none()

    if tag is None:
        _tag = Tag(tag_name=tag_name, tag_args=tag_args)
        session.add(_tag)
        await session.flush()
        tag = int(cast(int, _tag.data_id))

    return tag


__all__ = ["get_or_create_tag"]
