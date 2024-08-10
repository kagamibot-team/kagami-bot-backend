from src.core.unit_of_work import UnitOfWork


class PoolService:
    """
    关于卡池有关的机制，在这里统一用一个 Service 处理
    以免我出什么大的逻辑错误
    """

    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_current_pack(self, uid: int) -> int:
        """
        获得当前猎场
        """

        return await self.uow.user_pack.get_using(uid)

    async def get_aids(self, uid: int) -> set[int]:
        """
        获得用户当前使用的猎场中的所有的小哥
        """

        return await self.uow.awards.get_all_awards_in_pack(
            await self.get_current_pack(uid)
        )
    
    async def buy_pack(self, uid: int):
        """
        购买猎场
        """

    async def switch_pack(self, uid: int, name: str | None = None):
        """
        切换猎场
        """
