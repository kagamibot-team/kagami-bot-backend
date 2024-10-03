from datetime import timedelta

from src.common.times import now_datetime
from src.core.unit_of_work import UnitOfWork


class CDKeyService:
    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def clean(self, uid: int):
        await self.uow.cdkey.clear_attempts(uid, now_datetime() - timedelta(days=1))

    async def available(self, uid: int) -> bool:
        """
        检查 CDKey 可用性，如果不可用会抛出相关错误
        """
        await self.clean(uid)
        return len(await self.uow.cdkey.get_attempts(uid)) < 3

    async def claim(self, uid: int, cdkey: str): ...
