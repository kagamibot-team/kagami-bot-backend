from pydantic import BaseModel
from sqlalchemy import delete, func, insert, select, update
from typing_extensions import deprecated

from src.base.exceptions import ObjectNotFoundException
from src.base.res import KagamiResourceManagers
from src.models.models import SkinAltName
from src.ui.types.common import AwardInfo

from ..base.repository import DBRepository
from ..models.models import Skin


class SkinData(BaseModel):
    sid: int
    aid: int
    name: str
    description: str
    deprecated_price: float
    biscuit_price: int
    level: int

    can_draw: bool
    can_buy: bool

    def link(self, award_info: AwardInfo) -> AwardInfo:
        info = award_info.model_copy()
        info.sid = self.sid
        info.skin_name = self.name
        info._img_resource = KagamiResourceManagers.xiaoge(f"sid_{self.sid}.png")
        info.slevel = self.level
        info.description = self.description
        return info


class SkinRepository(DBRepository):
    """
    皮肤的仓库
    """

    async def delete(self, data_id: int) -> None:
        d = delete(Skin).where(Skin.data_id == data_id)
        await self.session.execute(d)

    @deprecated("皮肤系统已经进入 V2，这个函数不再使用")
    async def get_info(self, sid: int) -> tuple[str, str]:
        """获得一个皮肤的信息

        Args:
            sid (int): 皮肤的 ID

        Returns:
            tuple[str, str]: 名字，描述
        """
        q = select(Skin.name, Skin.description).filter(Skin.data_id == sid)
        return (await self.session.execute(q)).tuples().one()

    @deprecated("皮肤系统已经进入 V2，请逐一获取皮肤信息")
    async def all(self) -> list[tuple[int, int, str, str, float]]:
        """获得所有皮肤的信息

        Returns:
            list[tuple[int, int, str, str, float]]: 皮肤 ID，对应小哥 ID，名字，描述，价格
        """

        q = select(
            Skin.data_id,
            Skin.aid,
            Skin.name,
            Skin.description,
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

        q1 = select(Skin.data_id).where(func.lower(Skin.name) == name.lower())
        a = (await self.session.execute(q1)).scalar_one_or_none()
        if a is None:
            q2 = select(SkinAltName.skin_id).where(
                func.lower(SkinAltName.name) == name.lower()
            )
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
            raise ObjectNotFoundException("皮肤")
        return s

    async def create_skin(self, aid: int, name: str) -> int:
        """创建一个皮肤，注意这里会直接创建，请提前检查名字是否会重复

        Args:
            aid (int): 小哥的 ID
            name (str): 皮肤的名字

        Returns:
            int: 皮肤的 ID
        """

        q = (
            insert(Skin)
            .values({Skin.aid: aid, Skin.name: name})
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
            await self.session.execute(select(Skin.aid).filter(Skin.data_id == sid))
        ).scalar_one()

    async def get_all_sids_of_one_award(self, aid: int):
        """
        获得一个小哥含有的全部小哥
        """

        return set(
            (await self.session.execute(select(Skin.data_id).filter(Skin.aid == aid)))
            .scalars()
            .all()
        )

    @deprecated("请直接使用 SkinInfo.link 方法")
    async def link(self, sid: int, info: AwardInfo):
        q = select(Skin.name, Skin.description).filter(Skin.data_id == sid)
        sn, sd = (await self.session.execute(q)).tuples().one()
        if len(sd) > 0:
            info.description = sd
        info.skin_name = sn
        info.sid = sid

    async def get_info_v2(self, sid: int) -> SkinData:
        q = select(
            Skin.aid,
            Skin.name,
            Skin.description,
            Skin.price,
            Skin.biscuit,
            Skin.level,
            Skin.can_be_pulled,
            Skin.can_be_bought,
        ).filter(Skin.data_id == sid)

        res = (await self.session.execute(q)).tuples().one()

        return SkinData(
            sid=sid,
            aid=res[0],
            name=res[1],
            description=res[2],
            deprecated_price=res[3],
            biscuit_price=res[4],
            level=res[5],
            can_draw=res[6] == 1,
            can_buy=res[7] == 1,
        )

    async def set_info_v2(self, sid: int, info: SkinData) -> None:
        q = (
            update(Skin)
            .where(Skin.data_id == sid)
            .values(
                {
                    Skin.name: info.name,
                    Skin.description: info.description,
                    Skin.price: info.deprecated_price,
                    Skin.biscuit: info.biscuit_price,
                    Skin.level: info.level,
                    Skin.can_be_bought: int(info.can_buy),
                    Skin.can_be_pulled: int(info.can_draw),
                }
            )
        )
        await self.session.execute(q)

    async def all_sid(self) -> set[int]:
        q = select(Skin.data_id)
        return set((await self.session.execute(q)).scalars().all())

    async def get_all_sid_grouped_with_level(
        self, include_no_pickable: bool = False
    ) -> dict[int, set[int]]:
        q = select(Skin.data_id, Skin.level)
        if not include_no_pickable:
            q = q.filter(Skin.can_be_pulled == 1)
        result: dict[int, set[int]] = {}
        for sid, lid in (await self.session.execute(q)).tuples().all():
            result.setdefault(lid, set())
            result[lid].add(sid)

        return result

    async def get_all_sids_can_be_bought(self) -> set[int]:
        q = (
            select(Skin.data_id)
            .filter(Skin.can_be_bought == 1)
            .filter(Skin.biscuit > 0)
            .filter(Skin.level > 0)
        )
        return set((await self.session.execute(q)).scalars().all())
