from typing import Literal
from src.core.unit_of_work import UnitOfWork


class StatService:
    """
    和统计有关的服务
    """

    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    # 记录层：记录各类数据
    async def throw_baba(self, uid: int, target: int, success: bool):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="丢粑粑",
            linked_uid=target,
        )
        await self.uow.stats.update(stid, 1)
        if success:
            stid = await self.uow.stats.get_id(
                uid=uid,
                stat_type="丢粑粑成功",
                linked_uid=target,
            )
            await self.uow.stats.update(stid, 1)

    # 获取层：获得各类数据
    async def count_throw_baba(
        self,
        uid: int | Literal["no_limit"] = "no_limit",
        target: int | Literal["no_limit"] = "no_limit",
        success: bool | None = None,
    ) -> int:
        if success is None:
            return await self.uow.stats.get_sum(
                uid=uid,
                stat_type="丢粑粑",
                linked_uid=target,
            )
        if success:
            return await self.uow.stats.get_sum(
                uid=uid,
                stat_type="丢粑粑成功",
                linked_uid=target,
            )

        return await self.uow.stats.get_sum(
            uid=uid,
            stat_type="丢粑粑",
            linked_uid=target,
        ) - await self.uow.stats.get_sum(
            uid=uid,
            stat_type="丢粑粑成功",
            linked_uid=target,
        )
