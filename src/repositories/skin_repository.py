from pathlib import Path

from sqlalchemy import delete, insert, select, update

from src.base.exceptions import ObjectNotFoundException
from src.models.models import SkinAltName
from src.ui.views.award import AwardInfo

from ..base.repository import DBRepository
from ..models.models import Skin


class SkinRepository(DBRepository):
    """
    皮肤的仓库
    """

    async def delete(self, data_id: int) -> None:
        d = delete(Skin).where(Skin.data_id == data_id)
        await self.session.execute(d)

    async def get_all_images(self) -> dict[int, str]:
        qa = select(Skin.data_id, Skin.image)
        return {row[0]: row[1] for row in (await self.session.execute(qa)).tuples()}

    async def update_image(self, data_id: int, image: str | Path) -> None:
        u = (
            update(Skin)
            .where(Skin.data_id == data_id)
            .values({Skin.image: Path(image).as_posix()})
        )
        await self.session.execute(u)

    async def get_info(self, sid: int) -> tuple[str, str, str]:
        """获得一个皮肤的信息

        Args:
            sid (int): 皮肤的 ID

        Returns:
            tuple[str, str, str]: 名字，描述，图
        """
        q = select(Skin.name, Skin.description, Skin.image).filter(Skin.data_id == sid)
        return (await self.session.execute(q)).tuples().one()

    async def all(self) -> list[tuple[int, int, str, str, str, float]]:
        """获得所有皮肤的信息

        Returns:
            tuple[int, int, str, str, str, float]: 皮肤 ID，对应小哥 ID，名字，描述，图，价格
        """

        q = select(
            Skin.data_id,
            Skin.award_id,
            Skin.name,
            Skin.description,
            Skin.image,
            Skin.price,
        )
        return list((await self.session.execute(q)).tuples().all())

    async def get_sid(self, name: str) -> int | None:
        """根据名字获得皮肤的 ID

        Args:
            name (str): 名字

        Returns:
            int | None: 皮肤的 ID，不存在则为 None
        """

        q1 = select(Skin.data_id).where(Skin.name == name)
        a = (await self.session.execute(q1)).scalar_one_or_none()
        if a is None:
            q2 = select(SkinAltName.skin_id).where(SkinAltName.name == name)
            a = (await self.session.execute(q2)).scalar_one_or_none()

        return a

    async def get_sid_strong(self, name: str) -> int:
        """根据名字获得皮肤的 ID，如果不存在会抛出异常

        Args:
            name (str): 皮肤的名字

        Returns:
            int: 皮肤的 ID
        """
        s = await self.get_sid(name)
        if s is None:
            raise ObjectNotFoundException("皮肤", name)
        return s

    async def add_skin(self, aid: int, name: str) -> int:
        """创建一个皮肤，注意这里会直接创建，请提前检查名字是否会重复

        Args:
            aid (int): 小哥的 ID
            name (str): 皮肤的名字

        Returns:
            int: 皮肤的 ID
        """

        q = (
            insert(Skin)
            .values({Skin.award_id: aid, Skin.name: name})
            .returning(Skin.data_id)
        )
        return (await self.session.execute(q)).scalar_one()

    async def set_alias(self, sid: int, name: str):
        """设置一个皮肤的别名

        Args:
            sid (int): 皮肤的 ID
            name (str): 别名
        """
        await self.session.execute(
            insert(SkinAltName).values(
                {
                    SkinAltName.skin_id: sid,
                    SkinAltName.name: name,
                }
            )
        )

    async def remove_alias(self, name: str):
        """删除一个皮肤的别名

        Args:
            name (str): 别名
        """

        await self.session.execute(delete(SkinAltName).where(SkinAltName.name == name))

    async def get_aid(self, sid: int):
        """获得一个皮肤对应的小哥 ID

        Args:
            sid (int): 皮肤 ID
        """

        return (
            await self.session.execute(
                select(Skin.award_id).filter(Skin.data_id == sid)
            )
        ).scalar_one()

    async def get_all_sids_of_one_award(self, aid: int):
        """
        获得一个小哥含有的全部小哥
        """

        return set(
            (
                await self.session.execute(
                    select(Skin.data_id).filter(Skin.award_id == aid)
                )
            )
            .scalars()
            .all()
        )

    async def link(self, sid: int, info: AwardInfo):
        """
        更改 AwardInfo，挂载皮肤的信息
        """
        q = select(Skin.name, Skin.description, Skin.image)
        sn, sd, si = (await self.session.execute(q)).tuples().one()
        info.sid = sid
        info.skin_name = sn
        info.skin_description = sd
        info.skin_image = Path(si).name
