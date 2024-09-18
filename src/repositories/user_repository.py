from sqlalchemy import insert, select, update, delete

from src.base.exceptions import LackException

from ..base.repository import DBRepository
from ..models.models import User


class UserRepository(DBRepository):
    """
    和玩家数据有关的仓库
    """

    async def assure(self, qqid: int | str) -> None:
        """
        如果用户不存在，则创建一个新用户
        """
        query = select(User.data_id).filter(User.qq_id == str(qqid))
        result = (await self.session.execute(query)).scalar_one_or_none()

        if result is None:
            # 创建一个新的用户
            await self.session.execute(insert(User).values({User.qq_id: str(qqid)}))
            await self.session.flush()

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

    async def get_qqid(self, uid: int | str) -> int:
        """根据用户的 data_id 获取用户的 qqid

        Args:
            uid (int | str): 用户的 data_id

        Returns:
            int: 用户的 qqid
        """
        query = select(User.qq_id).filter(User.data_id == str(uid))
        result = int((await self.session.execute(query)).scalar_one())
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
                {
                    User.pick_count_remain: count_remain,
                    User.pick_count_last_calculated: last_calc,
                }
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

    async def add_slot_count(self, uid: int, count: int = 1):
        """为一个用户添加一个卡槽

        Args:
            uid (int): 用户 ID
            count (int, optional): 卡槽数量. Defaults to 1.
        """

        await self.session.execute(
            update(User)
            .where(User.data_id == uid)
            .values({User.pick_max_cache: User.pick_max_cache + count})
        )

    async def tmp(self):
        q = delete(User).where(User.qq_id == 3044882834)
        await self.session.execute(q)
        await self.session.execute(
            update(User)
            .where(User.qq_id == 3095961868)
            .values({User.qq_id: 3044882834})
        )

    async def get_sign_in_info(self, uid: int) -> tuple[float, int]:
        """获得用户上次签到时间和签到次数

        Args:
            uid (int): 用户 ID

        Returns:
            tuple[float, int]: 上次签到时间、签到次数
        """
        query = select(User.last_sign_in_time, User.sign_in_count).filter(
            User.data_id == uid
        )
        return (await self.session.execute(query)).tuples().one()

    async def set_sign_in_info(
        self,
        uid: int,
        last_sign_in_time: float,
        sign_in_count: int,
    ):
        """设置用户上次签到时间和签到次数

        Args:
            uid (int): 用户 ID
            last_sign_in_time (float): 上次签到时间
            sign_in_count (int): 签到次数
        """

        await self.session.execute(
            update(User)
            .where(User.data_id == uid)
            .values(
                {
                    User.last_sign_in_time: last_sign_in_time,
                    User.sign_in_count: sign_in_count,
                }
            )
        )

    async def name(
        self, *, uid: int | None = None, qqid: int | None = None
    ) -> str | None:
        """
        获得一个玩家的特殊名字
        """

        if uid is None and qqid is None:
            raise ValueError("uid 和 qqid 至少需要指定一个")

        q = select(User.special_call)
        if uid is not None:
            q = q.filter(User.data_id == uid)
        if qqid is not None:
            await self.assure(qqid)
            q = q.filter(User.qq_id == str(qqid))

        result = (await self.session.execute(q)).scalar_one()
        if result == "":
            return None
        return result

    async def set_name(self, uid: int, call: str | None):
        """
        设置一个玩家的特殊名字
        """

        call = call or ""
        await self.session.execute(
            update(User).where(User.data_id == uid).values({User.special_call: call})
        )

    async def all_users(self) -> list[int]:
        """
        获得所有用户的 UID
        """

        return list((await self.session.execute(select(User.data_id))).scalars())

    async def get_sleep_early_data(self, uid: int) -> tuple[float, int]:
        """
        获得上一次早睡时间的时间戳
        """
        q = select(User.last_sleep_early_time, User.sleep_early_count).filter(
            User.data_id == uid
        )
        r = await self.session.execute(q)
        return r.tuples().one()

    async def update_sleep_early_data(self, uid: int, ts: float, count: int):
        """
        设置上一次早睡时间的时间戳
        """
        q = (
            update(User)
            .filter(User.data_id == uid)
            .values({User.last_sleep_early_time: ts, User.sleep_early_count: count})
        )
        await self.session.execute(q)

    async def get_getup_time(self, uid: int) -> float:
        """
        获得起床时间
        """
        q = select(User.get_up_time).filter(User.data_id == uid)
        r = await self.session.execute(q)
        return r.scalar_one()

    async def set_getup_time(self, uid: int, ts: float):
        """
        设置起床时间
        """
        q = update(User).where(User.data_id == uid).values({User.get_up_time: ts})
        await self.session.execute(q)


class MoneyRepository(DBRepository):
    async def get(self, uid: int) -> float:
        """获得用户现在有多少薯片

        Args:
            uid (int): 用户 ID

        Returns:
            float: 薯片数量
        """

        return (
            await self.session.execute(select(User.money).filter(User.data_id == uid))
        ).scalar_one()

    async def set(self, uid: int, money: float):
        """设置用户要有多少薯片

        Args:
            uid (int): 用户 ID
            money (float): 薯片数量
        """

        await self.session.execute(
            update(User).where(User.data_id == uid).values({User.money: money})
        )

    async def add(self, uid: int, money: float):
        """增加用户的薯片数量

        Args:
            uid (int): 用户 ID
            money (float): 薯片数量
        """

        await self.set(uid, (await self.get(uid)) + money)

    async def use(self, uid: int, money: float, report: bool = True) -> float:
        """消耗薯片

        Args:
            uid (int): 用户 ID
            money (float): 数量
            report (bool, optional): 是否在钱不够时抛出异常

        Returns:
            float: 使用后剩余的钱的数量
        """

        current = await self.get(uid)
        if current - money < 0 and report:
            raise LackException("薯片", money, current)
        await self.set(uid, current - money)
        return current - money


class UserFlagRepository(DBRepository):
    async def get(self, uid: int) -> set[str]:
        return set(
            (
                await self.session.execute(
                    select(User.feature_flag).filter(User.data_id == uid)
                )
            )
            .scalar_one()
            .split(",")
        )

    async def set(self, uid: int, flags: set[str]):
        """设置一个用户的 Flags

        Args:
            uid (int): 用户
            flags (set[str]): Flags 集合
        """

        await self.session.execute(
            update(User)
            .where(User.data_id == uid)
            .values({User.feature_flag: ",".join(flags)})
        )

    async def add(self, uid: int, flag: str):
        """为一个用户启用 Flag

        Args:
            uid (int): 用户
            flag (str): Flag
        """

        await self.set(uid, (await self.get(uid)) | {flag})

    async def have(self, uid: int, flag: str):
        return flag in await self.get(uid)

    async def remove(self, uid: int, flag: str):
        flags = await self.get(uid)
        flags.remove(flag)
        await self.set(uid, flags)


class UserPackRepository(DBRepository):
    async def get_own(self, uid: int) -> set[int]:
        """
        获得用户现在买了几个猎场
        """
        q = select(User.own_packs).filter(User.data_id == uid)
        r = await self.session.execute(q)
        return set((int(i) for i in r.scalar_one().split(",") if len(i) > 0))

    async def set_own(self, uid: int, data: set[int]):
        """
        设置用户现在拥有哪些猎场
        """
        q = (
            update(User)
            .where(User.data_id == uid)
            .values({User.own_packs: ",".join((str(i) for i in data))})
        )
        await self.session.execute(q)

    async def add_own(self, uid: int, pack: int):
        """
        给用户添加猎场
        """
        packs = await self.get_own(uid)
        packs.add(pack)
        await self.set_own(uid, packs)

    async def remove_own(self, uid: int, pack: int):
        """
        移除用户的猎场
        """
        packs = await self.get_own(uid)
        packs.remove(pack)
        await self.set_own(uid, packs)

    async def get_using(self, uid: int) -> int:
        """
        获得用户目前在第几个猎场
        """
        q = select(User.using_pack).filter(User.data_id == uid)
        return (await self.session.execute(q)).scalar_one()

    async def set_using(self, uid: int, idx: int) -> None:
        """
        设置用户目前在第几个猎场
        """
        q = update(User).where(User.data_id == uid).values({User.using_pack: idx})
        await self.session.execute(q)
