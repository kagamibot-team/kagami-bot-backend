from src.core.unit_of_work import UnitOfWork


class PoolService:
    """
    关于卡池有关的机制，在这里统一用一个 Service 处理
    以免我出什么大的逻辑错误
    """

    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

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
                own_packs.remove(pack)
        await self.uow.user_pack.set_own(uid, own_packs)

        # 验证2: 用户不能处于自己没买的猎场
        if current_pack not in own_packs:
            current_pack = 1
            await self.uow.user_pack.set_using(uid, current_pack)

        # 验证3: 用户不能挂载没有激活的 / 自己没有的 / 不在当前猎场的猎场升级
        if current_up is not None:
            info = await self.uow.up_pool.get_pool_info(current_up)
            if (
                not info.enabled
                or info.belong_pack != current_pack
                or not current_pack in await self.uow.up_pool.get_own(uid)
            ):
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
