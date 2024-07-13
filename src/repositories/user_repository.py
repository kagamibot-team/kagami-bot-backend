from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.exceptions import LackException

from ..base.repository import DBRepository
from ..models import User


class UserRepository(DBRepository[User]):
    """
    和玩家数据有关的仓库
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def assure(self, qqid: int | str) -> None:
        """
        如果用户不存在，则创建一个新用户
        """
        query = select(User.data_id).filter(User.qq_id == str(qqid))
        result = (await self.session.execute(query)).scalar_one_or_none()

        if result is None:
            # 创建一个新的用户
            user = User(qqid=str(qqid))
            await self.add(user)

    async def get_uid(self, qqid: int | str) -> int:
        """根据用户的 qqid 获取用户的 data_id

        Args:
            qqid (int | str): 用户的 qqid

        Returns:
            int: 用户的 data_id
        """
        await self.assure(qqid)
        query = select(User.data_id).filter(User.qq_id == str(qqid))
        result = (await self.session.execute(query)).scalar_one()
        return result

    async def update_catch_time(self, uid: int, count_remain: int, last_calc: float):
        """更新玩家抓小哥的时间

        Args:
            uid (int): 用户的 data_id
            count_remain (int): 还有多少次抓小哥的次数
            last_calc (float): 上一次计算抓的时间
        """
        await self.session.execute(
            update(User)
            .where(User.data_id == uid)
            .values(
                pick_count_remain=count_remain, pick_count_last_calculated=last_calc
            )
        )

    async def get_catch_time_data(self, uid: int) -> tuple[int, int, float]:
        """获得玩家抓小哥的时间数据

        Args:
            uid (int): 玩家的 uid

        Returns:
            tuple[int, int, float]: 分别是卡槽数、剩余次数、上次计算时间
        """
        return (
            (
                await self.session.execute(
                    select(
                        User.pick_max_cache,
                        User.pick_count_remain,
                        User.pick_count_last_calculated,
                    ).where(User.data_id == uid)
                )
            )
            .tuples()
            .one()
        )

    async def get_flags(self, uid: int) -> set[str]:
        return set(
            (
                await self.session.execute(
                    select(User.feature_flag).filter(User.data_id == uid)
                )
            )
            .scalar_one()
            .split(",")
        )

    async def do_have_flag(self, uid: int, flag: str):
        return flag in await self.get_flags(uid)

    async def get_money(self, uid: int) -> float:
        """获得用户现在有多少薯片

        Args:
            uid (int): 用户 ID

        Returns:
            float: 薯片数量
        """

        return (
            await self.session.execute(select(User.money).filter(User.data_id == uid))
        ).scalar_one()

    async def set_money(self, uid: int, money: float):
        """设置用户要有多少薯片

        Args:
            uid (int): 用户 ID
            money (float): 薯片数量
        """

        await self.session.execute(
            update(User).where(User.data_id == uid).values(money=money)
        )

    async def use_money(self, uid: int, money: float, report: bool = True) -> float:
        """消耗薯片

        Args:
            uid (int): 用户 ID
            money (float): 数量
            report (bool, optional): 是否在钱不够时抛出异常

        Returns:
            float: 使用后剩余的钱的数量
        """

        current = await self.get_money(uid)
        if current - money < 0 and report:
            raise LackException("薯片", money, current)
        await self.set_money(uid, current - money)
        return current - money
