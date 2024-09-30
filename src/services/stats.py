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

    # 表层
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

    async def zhua(self, uid: int, aid: int, pid: int, count: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="抓到小哥",
            linked_aid=aid,
            linked_pid=pid,
        )
        await self.uow.stats.update(stid, count)

    async def zhua_get_chips(self, uid: int, count: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="在抓小哥的时候得到薯片",
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

    async def hc(self, uid: int, rid: int, success: bool, result: int, spent: int):
        _res = None if result < 0 else result
        msg = ({False: "合成失败", True: "合成成功"})[success]
        stid1 = await self.uow.stats.get_id(
            uid=uid,
            stat_type=msg,
            linked_rid=rid,
            linked_aid=_res,
        )
        await self.uow.stats.update(stid1, 1)
        msg = ({False: "合成失败消费", True: "合成成功消费"})[success]
        stid2 = await self.uow.stats.get_id(
            uid=uid,
            stat_type=msg,
            linked_rid=rid,
            linked_aid=_res,
        )
        await self.uow.stats.update(stid2, spent)
        return stid1, stid2

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
        stid = await self.uow.stats.get_id(uid=uid, stat_type="签到")
        await self.uow.stats.update(stid, 1)

    async def qhlc_command(self, uid: int, pid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="切换猎场",
            linked_pid=pid,
        )
        await self.uow.stats.update(stid, 1)

    async def check_lc_view(self, uid: int, pid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="看猎场的界面",
            linked_pid=pid,
        )
        await self.uow.stats.update(stid, 1)

    async def xjshop_buy(self, uid: int, spent: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="在小镜商店消费次数",
        )
        await self.uow.stats.update(stid, 1)
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="在小镜商店消费薯片",
        )
        await self.uow.stats.update(stid, spent)

    async def check_xjshop(self, uid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="查看小镜商店",
        )
        await self.uow.stats.update(stid, 1)

    async def switch_skin(self, uid: int, aid: int, sid: int | None):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="切换皮肤",
            linked_aid=aid,
            linked_sid=sid,
        )
        await self.uow.stats.update(stid, 1)

    async def shi(self, uid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="是",
        )
        await self.uow.stats.update(stid, 1)

    async def kbs(self, uid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="kbs",
        )
        await self.uow.stats.update(stid, 1)

    async def display(self, uid: int | None, aid: int, sid: int | None):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="展示小哥",
            linked_aid=aid,
            linked_sid=sid,
        )
        await self.uow.stats.update(stid, 1)

    async def poke(self, uid: int):
        stid = await self.uow.stats.get_id(
            uid=uid,
            stat_type="戳小镜",
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
