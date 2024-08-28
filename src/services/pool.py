from src.base.exceptions import (
    DoNotHaveException,
    ObjectNotFoundException,
    SoldOutException,
)
from src.core.unit_of_work import UnitOfWork
from src.repositories.up_pool_repository import UpPoolInfo
from loguru import logger


class PoolService:
    """
    关于卡池有关的机制，在这里统一用一个 Service 处理
    以免我出什么大的逻辑错误
    """

    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    # 底层机制之：需要获取的那些数据

    async def ensure_user(self, uid: int):
        """
        处理一遍用户的数据，如果有猎场 / 猎场升级的数据不匹配，
        就切换回默认的数据，防止在抓小哥时出现逻辑问题
        """

        current_up = await self.uow.up_pool.get_using(uid)
        current_pack = await self.uow.user_pack.get_using(uid)
        own_packs = await self.uow.user_pack.get_own(uid)

        max_count = await self.uow.settings.get_pack_count()

        # 验证1: 用户不能拥有超过系统设定的猎场的量
        for pack in own_packs:
            if pack > max_count:
                logger.warning(f"用户 {uid} 拥有 {pack}，但这个猎场并未开放")
                own_packs.remove(pack)

        # 验证2: 用户至少有一个猎场
        if len(own_packs) == 0 or 1 not in own_packs:
            logger.warning(f"用户 {uid} 没有 1 猎场，已默认赐予它一个猎场")
            own_packs.add(1)
        await self.uow.user_pack.set_own(uid, own_packs)

        # 验证3: 用户不能处于自己没买的猎场
        if current_pack not in own_packs:
            logger.warning(f"用户 {uid} 在自己没有买的猎场中")
            current_pack = 1
            await self.uow.user_pack.set_using(uid, current_pack)

        # 验证4: 用户不能挂载没有激活的 / 自己没有的 / 不在当前猎场的猎场升级
        if current_up is not None:
            info = await self.uow.up_pool.get_pool_info(current_up)
            if (
                (not info.enabled)
                or (info.belong_pack != current_pack)
                or (current_up not in await self.uow.up_pool.get_own(uid))
            ):
                logger.warning(f"用户 {uid} 挂载的猎场up和当前猎场不符")
                await self.uow.up_pool.set_using(uid, None)

    async def get_current_pack(self, uid: int) -> int:
        """
        获得一个用户当前的猎场
        """
        await self.ensure_user(uid)
        return await self.uow.user_pack.get_using(uid)

    async def get_aids(self, uid: int) -> set[int]:
        """
        获得一个用户当前状态下能抓到的所有小哥
        """
        pack = await self.get_current_pack(uid)
        main_aids = await self.uow.pack.get_main_aids_of_pack(pack)
        zero_aids = await self.uow.pack.get_main_aids_of_pack(0)
        linked_aids = await self.uow.pack.get_linked_aids_of_pack(pack)

        return main_aids | zero_aids | linked_aids

    async def get_up_aids(self, uid: int) -> set[int]:
        """
        获得一个用户当前状态下概率 Up 的所有小哥
        """
        using_up = await self.uow.up_pool.get_using(uid)
        if using_up is None:
            return set()
        return await self.uow.up_pool.get_aids(using_up)

    async def get_target_aids(self, aid: int) -> set[int]:
        """
        获得合成结果的目标小哥集合
        """
        main_pack = await self.uow.pack.get_main_pack(aid)
        results = await self.uow.pack.get_main_aids_of_pack(0)
        if main_pack > 0:
            results |= await self.uow.pack.get_main_aids_of_pack(main_pack)
        return results

    async def get_uncatchable_aids(self) -> set[int]:
        """
        获得所有抓不到的小哥的 ID
        """
        negative_main_aids = await self.uow.pack.get_aids_without_main_pack()
        no_relationship = await self.uow.pack.get_aids_without_relationship()
        return negative_main_aids & no_relationship

    async def get_buyable_pool(self, pack: int) -> int | None:
        """
        获得一个猎场可以购买的猎场升级
        """
        pools = await self.uow.up_pool.get_pools_of_pack(pack, require_enabled=True)
        assert len(pools) <= 1
        if len(pools) == 0:
            return None
        return pools.pop()

    # 上层机制之：用户的各种对小L猎场的操 作

    async def switch_pack(self, uid: int, pack: int | None = None) -> int:
        """
        切换猎场，返回切换以后的猎场序号
        """

        current = await self.get_current_pack(uid)
        available = list(await self.uow.user_pack.get_own(uid))
        max_count = await self.uow.settings.get_pack_count()
        assert len(available) > 0
        if pack is not None:
            if pack <= 0 or pack > max_count:
                raise ObjectNotFoundException("猎场")
            if pack not in available:
                raise DoNotHaveException("猎场")
        elif len(available) == 1 or current not in available:
            pack = available[0]
        else:
            idx = available.index(current)
            idx += 1
            idx %= len(available)
            pack = available[idx]
        await self.uow.user_pack.set_using(uid, pack)
        return pack

    async def buy_pack(self, uid: int, pack_id: int):
        """
        购买一个猎场（失败就抛出异常）
        """

        max_count = await self.uow.settings.get_pack_count()
        own_packs = await self.uow.user_pack.get_own(uid)

        if pack_id in own_packs:
            raise SoldOutException(f"{pack_id} 号猎场")
        if pack_id <= 0 or pack_id > max_count:
            raise ObjectNotFoundException("猎场")

        await self.uow.money.use(uid, 1000)
        await self.uow.user_pack.add_own(uid, pack_id)

    async def toggle_up_pool(self, uid: int) -> int | None:
        """
        切换猎场升级，返回使用的猎场升级的 ID
        """

        await self.ensure_user(uid)
        current_pack = await self.uow.user_pack.get_using(uid)
        pools = list(await self.uow.up_pool.get_own(uid, current_pack))
        using = await self.uow.up_pool.get_using(uid)

        if len(pools) == 0:
            raise DoNotHaveException(f"{current_pack} 号猎场的猎场升级")

        if using is None:
            res = pools[0]
        elif using == pools[-1]:
            res = None
        else:
            res = pools[pools.index(using) + 1]

        await self.uow.up_pool.set_using(uid, res)
        return res

    async def buy_up_pool(self, uid: int) -> UpPoolInfo:
        """
        购买一个猎场的猎场升级
        """

        pack = await self.get_current_pack(uid)
        await self.ensure_user(uid)
        upid = await self.get_buyable_pool(pack)
        if upid is None:
            raise ObjectNotFoundException("猎场的猎场升级")
        if upid in await self.uow.up_pool.get_own(uid, pack):
            raise SoldOutException(f"{pack} 号猎场的猎场升级")
        info = await self.uow.up_pool.get_pool_info(upid)
        await self.uow.money.use(uid, info.cost)
        await self.uow.up_pool.add_own(uid, upid)
        return info

    # 管理员指令

    async def hang_up_pool(self, name: str) -> bool:
        """
        将一个 Up 池挂载上来，返回更改以后是否被挂载上来了
        """
        upid = await self.uow.up_pool.get_upid_strong(name)
        info = await self.uow.up_pool.get_pool_info(upid)
        pack = info.belong_pack
        pools = await self.uow.up_pool.get_pools_of_pack(pack)

        result = True

        for pool in pools:
            if await self.uow.up_pool.is_pool_hangup(pool):
                await self.uow.up_pool.modify(pool, enabled=False)
                if pool == upid:
                    result = False
            elif pool == upid:
                await self.uow.up_pool.modify(pool, enabled=True)

        return result

    async def add_award_linked_pack(self, name: str, pack: int):
        """
        给一个小哥添加一个关联猎场
        """
        assert pack > 0
        aid = await self.uow.awards.get_aid_strong(name)
        await self.uow.pack.add_linked_pack(aid, pack)

    async def remove_award_linked_pack(self, name: str, pack: int):
        """
        移除一个小哥的关联猎场
        """
        aid = await self.uow.awards.get_aid_strong(name)
        await self.uow.pack.remove_linked_pack(aid, pack)
