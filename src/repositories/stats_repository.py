from typing import Iterable, Literal

from pydantic import BaseModel
from sqlalchemy import func, insert, select, update

from src.base.repository import DBRepository
from src.models.stats import StatRecord


class StatData(BaseModel):
    uid: int
    stat_type: str
    count: int
    linked_uid: int
    linked_aid: int
    linked_sid: int
    linked_pid: int
    linked_rid: int
    linked_upid: int


class StatsRepository(DBRepository):
    """
    统计数据
    """

    async def _create(
        self,
        uid: int,
        stat_type: str,
        count: int = 0,
        linked_uid: int | None = None,
        linked_aid: int | None = None,
        linked_sid: int | None = None,
        linked_pid: int | None = None,
        linked_rid: int | None = None,
        linked_upid: int | None = None,
    ) -> None:
        """
        创建一个新的统计字段
        """
        await self.session.execute(
            insert(StatRecord).values(
                {
                    StatRecord.stat_from: uid,
                    StatRecord.stat_type: stat_type,
                    StatRecord.count: count,
                    StatRecord.linked_uid: linked_uid,
                    StatRecord.linked_aid: linked_aid,
                    StatRecord.linked_sid: linked_sid,
                    StatRecord.linked_pid: linked_pid,
                    StatRecord.linked_rid: linked_rid,
                    StatRecord.linked_upid: linked_upid,
                }
            )
        )
        await self.session.flush()

    async def _get(
        self,
        uid: int,
        stat_type: str,
        linked_uid: int | None = None,
        linked_aid: int | None = None,
        linked_sid: int | None = None,
        linked_pid: int | None = None,
        linked_rid: int | None = None,
        linked_upid: int | None = None,
    ) -> int | None:
        """
        获得一个统计数据的 ID
        """

        query = (
            select(StatRecord.data_id, StatRecord.count)
            .filter(StatRecord.stat_from == uid, StatRecord.stat_type == stat_type)
            .filter(StatRecord.linked_uid == linked_uid)
            .filter(StatRecord.linked_aid == linked_aid)
            .filter(StatRecord.linked_sid == linked_sid)
            .filter(StatRecord.linked_pid == linked_pid)
            .filter(StatRecord.linked_rid == linked_rid)
            .filter(StatRecord.linked_upid == linked_upid)
        )

        res = await self.session.execute(query)
        return res.scalar_one_or_none()

    async def get_all_id(
        self,
        uid: int | Literal["no_limit"],
        stat_type: str,
        linked_uid: int | None | Literal["no_limit"] = "no_limit",
        linked_aid: int | None | Literal["no_limit"] = "no_limit",
        linked_sid: int | None | Literal["no_limit"] = "no_limit",
        linked_pid: int | None | Literal["no_limit"] = "no_limit",
        linked_rid: int | None | Literal["no_limit"] = "no_limit",
        linked_upid: int | None | Literal["no_limit"] = "no_limit",
    ) -> list[int]:
        """
        获得很多统计数据的 ID
        """

        query = select(StatRecord.data_id, StatRecord.count).filter(
            StatRecord.stat_type == stat_type
        )

        query = (
            query if uid == "no_limit" else query.filter(StatRecord.stat_from == uid)
        )
        query = (
            query
            if linked_uid == "no_limit"
            else query.filter(StatRecord.linked_uid == linked_uid)
        )
        query = (
            query
            if linked_aid == "no_limit"
            else query.filter(StatRecord.linked_aid == linked_aid)
        )
        query = (
            query
            if linked_sid == "no_limit"
            else query.filter(StatRecord.linked_sid == linked_sid)
        )
        query = (
            query
            if linked_pid == "no_limit"
            else query.filter(StatRecord.linked_pid == linked_pid)
        )
        query = (
            query
            if linked_rid == "no_limit"
            else query.filter(StatRecord.linked_rid == linked_rid)
        )
        query = (
            query
            if linked_upid == "no_limit"
            else query.filter(StatRecord.linked_upid == linked_upid)
        )

        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def assure(
        self,
        uid: int,
        stat_type: str,
        linked_uid: int | None = None,
        linked_aid: int | None = None,
        linked_sid: int | None = None,
        linked_pid: int | None = None,
        linked_rid: int | None = None,
        linked_upid: int | None = None,
    ):
        _id = await self._get(
            uid=uid,
            stat_type=stat_type,
            linked_uid=linked_uid,
            linked_aid=linked_aid,
            linked_sid=linked_sid,
            linked_pid=linked_pid,
            linked_rid=linked_rid,
            linked_upid=linked_upid,
        )
        if _id is None:
            await self._create(
                uid=uid,
                stat_type=stat_type,
                linked_uid=linked_uid,
                linked_aid=linked_aid,
                linked_sid=linked_sid,
                linked_pid=linked_pid,
                linked_rid=linked_rid,
                linked_upid=linked_upid,
            )

    async def get_sum(
        self,
        uid: int | Literal["no_limit"],
        stat_type: str,
        linked_uid: int | None | Literal["no_limit"] = "no_limit",
        linked_aid: int | None | Literal["no_limit"] = "no_limit",
        linked_sid: int | None | Literal["no_limit"] = "no_limit",
        linked_pid: int | None | Literal["no_limit"] = "no_limit",
        linked_rid: int | None | Literal["no_limit"] = "no_limit",
        linked_upid: int | None | Literal["no_limit"] = "no_limit",
    ) -> int:
        query = select(func.sum(StatRecord.count)).filter(
            StatRecord.stat_type == stat_type
        )

        query = (
            query if uid == "no_limit" else query.filter(StatRecord.stat_from == uid)
        )
        query = (
            query
            if linked_uid == "no_limit"
            else query.filter(StatRecord.linked_uid == linked_uid)
        )
        query = (
            query
            if linked_aid == "no_limit"
            else query.filter(StatRecord.linked_aid == linked_aid)
        )
        query = (
            query
            if linked_sid == "no_limit"
            else query.filter(StatRecord.linked_sid == linked_sid)
        )
        query = (
            query
            if linked_pid == "no_limit"
            else query.filter(StatRecord.linked_pid == linked_pid)
        )
        query = (
            query
            if linked_rid == "no_limit"
            else query.filter(StatRecord.linked_rid == linked_rid)
        )
        query = (
            query
            if linked_upid == "no_limit"
            else query.filter(StatRecord.linked_upid == linked_upid)
        )

        res = await self.session.execute(query)
        return res.scalar_one()

    async def get_data_list(self, stat_ids: Iterable[int]) -> list[StatData]:
        query = select(
            StatRecord.stat_from,
            StatRecord.stat_type,
            StatRecord.count,
            StatRecord.linked_uid,
            StatRecord.linked_aid,
            StatRecord.linked_sid,
            StatRecord.linked_pid,
            StatRecord.linked_rid,
            StatRecord.linked_upid,
        ).filter(StatRecord.data_id.in_(stat_ids))

        data = (await self.session.execute(query)).tuples().all()
        result: list[StatData] = []

        for (
            uid,
            stat_type,
            count,
            linked_uid,
            linked_aid,
            linked_sid,
            linked_pid,
            linked_rid,
            linked_upid,
        ) in data:
            result.append(
                StatData(
                    uid=uid,
                    stat_type=stat_type,
                    count=count,
                    linked_uid=linked_uid,
                    linked_aid=linked_aid,
                    linked_sid=linked_sid,
                    linked_pid=linked_pid,
                    linked_rid=linked_rid,
                    linked_upid=linked_upid,
                )
            )

        return result

    async def get_data(self, stat_id: int) -> StatData:
        return (await self.get_data_list((stat_id,)))[0]

    async def get_id(
        self,
        uid: int,
        stat_type: str,
        linked_uid: int | None = None,
        linked_aid: int | None = None,
        linked_sid: int | None = None,
        linked_pid: int | None = None,
        linked_rid: int | None = None,
        linked_upid: int | None = None,
    ) -> int:
        await self.assure(
            uid=uid,
            stat_type=stat_type,
            linked_uid=linked_uid,
            linked_aid=linked_aid,
            linked_sid=linked_sid,
            linked_pid=linked_pid,
            linked_rid=linked_rid,
            linked_upid=linked_upid,
        )
        result = await self._get(
            uid=uid,
            stat_type=stat_type,
            linked_uid=linked_uid,
            linked_aid=linked_aid,
            linked_sid=linked_sid,
            linked_pid=linked_pid,
            linked_rid=linked_rid,
            linked_upid=linked_upid,
        )
        assert result is not None
        return result

    async def update(self, stat_id: int, delta: int):
        query = (
            update(StatRecord)
            .where(StatRecord.data_id == stat_id)
            .values({StatRecord.count: StatRecord.count + delta})
        )
        await self.session.execute(query)
