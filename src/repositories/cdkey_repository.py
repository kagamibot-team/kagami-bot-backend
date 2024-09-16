from datetime import datetime

from sqlalchemy import delete, insert, select, update

from src.base.repository import DBRepository
from src.models.cdkey import CDKey, CDKeyBatch, CDKeyBatchAward, CDKeyUsage
from src.ui.types.cdkey import CDKeyBatchAwardData, CDKeyBatchMeta


class CDKeyRepository(DBRepository):
    # ------ #
    # 元数据 #
    # ------ #

    async def get_batch_meta_list(
        self,
        batch_ids: list[int] | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[CDKeyBatchMeta]:
        """
        获得 CDKey 的元数据列表
        """

        q = select(
            CDKeyBatch.data_id,
            CDKeyBatch.name,
            CDKeyBatch.max_redeem_limit,
            CDKeyBatch.expiration_date,
            CDKeyBatch.is_active,
        )

        if batch_ids is not None:
            q = q.filter(CDKeyBatch.data_id.in_(batch_ids))

        if page_size is not None:
            q = q.limit(page_size)
            if page is not None:
                q = q.offset((page - 1) * page_size)

        results: list[CDKeyBatchMeta] = []
        for batch_id, name, max_redeem_limit, expiration_date, is_active in (
            (await self.session.execute(q)).tuples().all()
        ):
            results.append(
                CDKeyBatchMeta(
                    batch_id=batch_id,
                    name=name,
                    max_redeem_limit=max_redeem_limit,
                    expiration_date=expiration_date,
                    is_active=is_active,
                )
            )

        return results

    async def get_batch_meta(self, batch_id: int) -> CDKeyBatchMeta:
        return (await self.get_batch_meta_list([batch_id]))[0]

    async def set_batch_meta(self, meta: CDKeyBatchMeta) -> None:
        q = (
            update(CDKeyBatch)
            .where(CDKeyBatch.data_id == meta.batch_id)
            .values(
                {
                    CDKeyBatch.name: meta.name,
                    CDKeyBatch.max_redeem_limit: meta.max_redeem_limit,
                    CDKeyBatch.expiration_date: meta.expiration_date,
                    CDKeyBatch.is_active: meta.is_active,
                }
            )
        )
        await self.session.execute(q)

    async def create_batch(
        self,
        name: str,
        max_redeem_limit: int | None = None,
        expiration_date: datetime | None = None,
        is_active: bool = False,
    ):
        q = insert(CDKeyBatch).values(
            {
                CDKeyBatch.name: name,
                CDKeyBatch.max_redeem_limit: max_redeem_limit,
                CDKeyBatch.expiration_date: expiration_date,
                CDKeyBatch.is_active: is_active,
            }
        )
        await self.session.execute(q)

    async def deleta_batch(self, batch_id: int) -> None:
        q = delete(CDKeyBatch).filter(CDKeyBatch.data_id == batch_id)
        await self.session.execute(q)

    # ---- #
    # 奖励 #
    # ---- #

    async def create_batch_award(
        self,
        batch_id: int,
        data: CDKeyBatchAwardData,
    ) -> None:
        if data.award_type == "award":
            q = insert(CDKeyBatchAward).values(
                {
                    CDKeyBatchAward.batch_id: batch_id,
                    CDKeyBatchAward.aid: data.data_id,
                    CDKeyBatchAward.quantity: data.quantity,
                }
            )
        elif data.award_type == "skin":
            q = insert(CDKeyBatchAward).values(
                {
                    CDKeyBatchAward.batch_id: batch_id,
                    CDKeyBatchAward.sid: data.data_id,
                }
            )
        else:
            q = insert(CDKeyBatchAward).values(
                {
                    CDKeyBatchAward.batch_id: batch_id,
                    CDKeyBatchAward.chips: data.quantity,
                }
            )
        await self.session.execute(q)

    async def get_awards_by_batch(self, batch_id: int) -> list[CDKeyBatchAwardData]:
        q = select(
            CDKeyBatchAward.aid,
            CDKeyBatchAward.sid,
            CDKeyBatchAward.chips,
            CDKeyBatchAward.quantity,
        ).filter(CDKeyBatchAward.batch_id == batch_id)

        results: list[CDKeyBatchAwardData] = []
        for aid, sid, chips, quantity in (await self.session.execute(q)).tuples().all():
            if aid is not None:
                results.append(
                    CDKeyBatchAwardData(
                        award_type="award", data_id=aid, quantity=quantity
                    )
                )
            elif sid is not None:
                results.append(CDKeyBatchAwardData(award_type="skin", data_id=sid))
            elif chips is not None:
                results.append(CDKeyBatchAwardData(award_type="chips", quantity=chips))
        return results

    async def delete_awards_by_batch(self, batch_id: int) -> None:
        q = delete(CDKeyBatchAward).filter(CDKeyBatchAward.batch_id == batch_id)
        await self.session.execute(q)

    # -------- #
    # CDK 管理 #
    # -------- #

    async def create_cdk(self, code: str, batch_id: int) -> None:
        q = insert(CDKey).values(
            {
                CDKey.batch_id: batch_id,
                CDKey.code: code,
            }
        )
        await self.session.execute(q)

    async def get_cdk_batch_id(self, code: str) -> int:
        q = select(CDKey.batch_id).filter(CDKey.code == code)
        r = await self.session.execute(q)
        return r.scalar_one()

    async def get_batch_cdks(self, batch_id: int) -> set[str]:
        q = select(CDKey.code).filter(CDKey.batch_id == batch_id)
        r = await self.session.execute(q)
        return set(r.scalars().all())

    async def delete_cdk(self, code: str) -> None:
        q = delete(CDKey).filter(CDKey.code == code)
        await self.session.execute(q)

    # ------------ #
    # CDK 使用记录 #
    # ------------ #

    async def create_usage(self, cdk_id: int, uid: int) -> None:
        q = insert(CDKeyUsage).values(
            {
                CDKeyUsage.cdk_id: cdk_id,
                CDKeyUsage.uid: uid,
            }
        )
        await self.session.execute(q)

    async def get_usage_uids(self, cdk_id: int) -> set[int]:
        q = select(CDKeyUsage.uid).filter(CDKeyUsage.cdk_id == cdk_id)
        r = await self.session.execute(q)
        return set(r.scalars().all())
