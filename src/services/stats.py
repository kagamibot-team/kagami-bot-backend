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

    async def zhua(self, uid: int, aid: int, pid: int, count: int = 1):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="抓到小哥",
            linked_aid=aid,
            linked_pid=pid,
        )
        await self.uow.stats.update(stid, count)

    async def zhua_command(self, uid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="进行一次抓",
        )
        await self.uow.stats.update(stid, 1)

    async def kz_command(self, uid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="进行一次狂抓",
        )
        await self.uow.stats.update(stid, 1)

    async def hc(self, uid: int, rid: int, success: bool, result: int):
        msg = ({
            False: "合成失败",
            True: "合成成功"
        })[success]
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type=msg,
            linked_rid=rid,
            linked_aid=result,
        )
        await self.uow.stats.update(stid, 1)

    async def sleep(self, uid: int, early: bool):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="小镜晚安",
        )
        await self.uow.stats.update(stid, 1)
        if early:
            stid = await self.uow.stats.get_id(
                uid=uid,
                stat_type="早睡",
            )
            await self.uow.stats.update(stid, 1)

    async def sign(self, uid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="签到"
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
