from pathlib import Path
from typing import Iterable, Sequence

from sqlalchemy import delete, insert, select, update

from src.base.exceptions import ObjectNotFoundException

from ..base.repository import DBRepository
from ..models.models import Award, AwardAltName


class AwardRepository(DBRepository):
    """
    小哥的仓库
    """

    async def get_all_images(self) -> dict[int, str]:
        """获得目前含有的所有图片

        Returns:
            dict[int, str]: 字典，是 Aid 到图片地址的字典
        """
        qa = select(Award.data_id, Award.image)
        return {row[0]: row[1] for row in (await self.session.execute(qa)).tuples()}

    async def update_image(self, data_id: int, image: str | Path) -> None:
        """更改小哥的图片

        Args:
            data_id (int): 小哥的 ID
            image (str | Path): 图片的地址
        """
        if not isinstance(image, str):
            image = image.as_posix()
        u = update(Award).where(Award.data_id == data_id).values(image=image)
        await self.session.execute(u)

    async def add_award(self, name: str, lid: int):
        """添加一个小哥

        Args:
            name (str): 名字
            lid (int): 等级

        Returns:
            int: 添加了的小哥的 ID
        """
        await self.session.execute(
            insert(Award).values(
                {
                    Award.level_id: lid,
                    Award.name: name,
                    Award.main_pack_id: -1,
                }
            )
        )
        await self.session.flush()

        return await self.get_aid_strong(name)

    async def get_aid(self, name: str) -> int | None:
        """根据名字找到一个小哥的 ID

        Args:
            name (str): 小哥的名字

        Returns:
            int | None: 结果。如果找不到，则返回 None
        """
        q1 = select(Award.data_id).where(Award.name == name)
        a = (await self.session.execute(q1)).scalar_one_or_none()
        if a is None:
            q2 = select(AwardAltName.award_id).where(AwardAltName.name == name)
            a = (await self.session.execute(q2)).scalar_one_or_none()

        return a

    async def get_aids(self, lid: int, pack: int | None = None) -> list[int]:
        """获得全部小哥

        Args:
            lid (int): 等级 ID
            pack (int): 猎场 ID

        Returns:
            list[int]: 小哥的 ID 列表
        """

        q = (
            select(Award.data_id)
            .filter(Award.level_id == lid)
            .order_by(-Award.sorting, Award.data_id)
        )
        if pack is not None:
            q = q.filter(Award.main_pack_id == pack)
        return [row[0] for row in (await self.session.execute(q)).tuples().all()]

    async def get_aid_strong(self, name: str) -> int:
        """强制获得一个小哥 ID，如果没有就报错

        Args:
            name (str): 小哥的名字

        Returns:
            int: 小哥的 ID
        """
        aid = await self.get_aid(name)
        if aid is None:
            raise ObjectNotFoundException("小哥", name)
        return aid

    async def get_info(self, aid: int) -> tuple[str, str, int, str, int, int]:
        """获取一个小哥的基础信息

        Args:
            aid (int): 小哥的 ID

        Returns:
            tuple[str, str, int, str, int, int]: 名字、描述、等级 ID 和图片，排序，是否抽得到
        """
        query = select(
            Award.name,
            Award.description,
            Award.level_id,
            Award.image,
            Award.sorting,
            Award.main_pack_id,
        ).filter(Award.data_id == aid)
        return (await self.session.execute(query)).tuples().one()

    async def set_alias(self, aid: int, name: str):
        """设置一个小哥的别名

        Args:
            aid (int): 小哥的 ID
            name (str): 别名
        """
        await self.session.execute(
            insert(AwardAltName).values(
                {
                    AwardAltName.award_id: aid,
                    AwardAltName.name: name,
                }
            )
        )

    async def remove_alias(self, name: str):
        """移除一个小哥的别名

        Args:
            name (str): 别名
        """
        await self.session.execute(
            delete(AwardAltName).where(AwardAltName.name == name)
        )

    async def delete_award(self, aid: int):
        """删除一个小哥

        Args:
            aid (int): 小哥的 ID
        """
        await self.session.execute(delete(Award).where(Award.data_id == aid))

    async def modify(
        self,
        aid: int,
        name: str | None = None,
        description: str | None = None,
        lid: int | None = None,
        image: str | Path | None = None,
        pack_id: int | None = None,
        sorting: int | None = None,
    ):
        """修改一个小哥的信息

        Args:
            aid (int): 小哥的 ID
            name (str | None): 名字
            description (str | None): 描述
            lid (int | None): 等级 ID
            image (str | Path | None): 图片
            pack_id (int | None): 小哥所在的猎场，0 代表所有，-1 代表不出现
            sorting (int | None): 排序的优先级
        """

        query = update(Award).where(Award.data_id == aid)
        if name is not None:
            query = query.values({Award.name: name})
        if description is not None and len(description) > 0:
            query = query.values({Award.description: description})
        if lid is not None:
            query = query.values({Award.level_id: lid})
        if image is not None:
            query = query.values({Award.image: Path(image).as_posix()})
        if pack_id is not None:
            query = query.values({Award.main_pack_id: pack_id})
        if sorting is not None:
            query = query.values({Award.sorting: sorting})

        await self.session.execute(query)

    async def group_by_level(self, aids: Iterable[int]) -> dict[int, set[int]]:
        """
        根据等级给小哥分类
        """

        result: dict[int, set[int]] = {}
        query = select(Award.data_id, Award.level_id).filter(Award.data_id.in_(aids))

        for aid, lid in (await self.session.execute(query)).tuples().all():
            result.setdefault(lid, set())
            result[lid].add(aid)

        return result

    async def get_lid(self, aid: int) -> int:
        """
        获得一个小哥的等级 ID
        """

        return (
            await self.session.execute(
                select(Award.level_id).filter(Award.data_id == aid)
            )
        ).scalar_one()

    async def get_list_of_award_info(
        self, aids: list[int]
    ) -> Sequence[tuple[int, str, str, int, str, int, int]]:
        """获取多个小哥的基础信息

        Args:
            aids (list[int]): 小哥的 ID 列表

        Returns:
            Sequence[tuple[int, str, str, int, str, int, int]]: 小哥 ID 和基础信息
        """

        query = select(
            Award.data_id,
            Award.name,
            Award.description,
            Award.level_id,
            Award.image,
            Award.main_pack_id,
            Award.sorting,
        ).where(Award.data_id.in_(aids))
        return (await self.session.execute(query)).tuples().all()

    async def get_all_mergeable_zeros(self) -> set[int]:
        """
        获得所有可以合成的零星小哥
        """
        q = select(Award.data_id).filter(Award.level_id == 0)
        r = await self.session.execute(q)
        return set(r.scalars())

    async def get_names(self, aids: Iterable[int]) -> dict[int, str]:
        """
        获得很多小哥的名字
        """
        q = select(Award.data_id, Award.name).filter(Award.data_id.in_(aids))
        r = await self.session.execute(q)
        return dict(r.tuples().all())
