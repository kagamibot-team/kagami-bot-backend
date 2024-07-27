from pathlib import Path
from typing import Sequence, cast

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.exceptions import ObjectNotFoundException

from ..base.repository import DBRepository
from ..models import Award, AwardAltName


class AwardRepository(DBRepository[Award]):
    """
    小哥的仓库
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Award)

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
        award = Award(level_id=lid, name=name)
        await self.add(award)
        await self.session.flush()

        return cast(int, award.data_id)

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

    async def get_aids(self, lid: int) -> list[int]:
        """根据等级 ID 获得所有该等级的小哥的 ID

        Args:
            lid (int): 等级 ID

        Returns:
            list[int]: 小哥的 ID 列表
        """

        q = (
            select(Award.data_id)
            .filter(Award.level_id == lid)
            .order_by(-Award.sorting, Award.data_id)
        )
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

    async def get_info(self, aid: int) -> tuple[str, str, int, str]:
        """获取一个小哥的基础信息

        Args:
            aid (int): 小哥的 ID

        Returns:
            tuple[str, str, int, str]: 名字、描述、等级 ID 和图片
        """
        query = select(
            Award.name,
            Award.description,
            Award.level_id,
            Award.image,
        ).filter(Award.data_id == aid)
        return (await self.session.execute(query)).tuples().one()

    async def set_alias(self, aid: int, name: str):
        """设置一个小哥的别名

        Args:
            aid (int): 小哥的 ID
            name (str): 别名
        """
        await self.session.execute(insert(AwardAltName).values(award_id=aid, name=name))

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
        special: bool | None = None,
        sorting: int | None = None,
    ):
        """修改一个小哥的信息

        Args:
            aid (int): 小哥的 ID
            name (str | None): 名字
            description (str | None): 描述
            lid (int | None): 等级 ID
            image (str | Path | None): 图片
            special (bool | None): 是否是特殊的小哥，即无法被抽到与合成到
            sorting (int | None): 排序的优先级
        """

        query = update(Award).where(Award.data_id == aid)
        if name is not None:
            query = query.values(name=name)
        if description is not None:
            query = query.values(description=description)
        if lid is not None:
            query = query.values(level_id=lid)
        if image is not None:
            query = query.values(image=Path(image).as_posix())
        if special is not None:
            query = query.values(is_special_get_only=special)
        if sorting is not None:
            query = query.values(sorting=sorting)

        await self.session.execute(query)

    async def get_list_of_award_info(
        self, aids: list[int]
    ) -> Sequence[tuple[int, str, str, int, str, bool, int]]:
        """获取多个小哥的基础信息

        Args:
            aids (list[int]): 小哥的 ID 列表

        Returns:
            Sequence[tuple[int, str, str, int, str, bool, int]]: 小哥 ID 和基础信息
        """

        query = select(
            Award.data_id,
            Award.name,
            Award.description,
            Award.level_id,
            Award.image,
            Award.is_special_get_only,
            Award.sorting,
        ).where(Award.data_id.in_(aids))
        return (await self.session.execute(query)).tuples().all()
