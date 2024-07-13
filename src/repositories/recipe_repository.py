from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..base.exceptions import RecipeMissing
from ..base.repository import BaseRepository
from ..models import Recipe


class RecipeRepository(BaseRepository[Recipe]):
    """
    小哥合成配方的仓库
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Recipe)

    async def get_recipe(
        self, aid1: int, aid2: int, aid3: int
    ) -> tuple[int, float] | None:
        """根据三个小哥获取数据库中的配方。如果没有生成过这个配方，则返回 None

        Args:
            aid1 (int): 第一个小哥的 ID
            aid2 (int): 第二个小哥的 ID
            aid3 (int): 第三个小哥的 ID

        Returns:
            tuple[int, float] | None: 如果存在配方，则返回 (成功合成的小哥, 成功率)，否则返回 None
        """

        # 配方是无序的，先排序

        aid1, aid2, aid3 = sorted([aid1, aid2, aid3])

        query = select(Recipe.result, Recipe.possibility).filter(
            Recipe.award1 == aid1, Recipe.award2 == aid2, Recipe.award3 == aid3
        )

        return (await self.session.execute(query)).tuples().one_or_none()

    async def add_recipe(
        self,
        aid1: int,
        aid2: int,
        aid3: int,
        aidres: int,
        possibility: float,
        modified: bool = False,
    ) -> None:
        """添加一个配方

        Args:
            aid1 (int): 第一个小哥的 ID
            aid2 (int): 第二个小哥的 ID
            aid3 (int): 第三个小哥的 ID
            aidres (int): 成功合成的小哥的 ID
            possibility (float): 成功率
        """
        aid1, aid2, aid3 = sorted([aid1, aid2, aid3])
        await self.add(
            Recipe(
                award1=aid1,
                award2=aid2,
                award3=aid3,
                result=aidres,
                possibility=possibility,
                modified=1 if modified else 0,
            )
        )

    async def update_recipe(
        self,
        aid1: int,
        aid2: int,
        aid3: int,
        aidres: int | None,
        possibility: float | None,
    ) -> None:
        """更新一个配方

        Args:
            aid1 (int): 第一个小哥的 ID
            aid2 (int): 第二个小哥的 ID
            aid3 (int): 第三个小哥的 ID
            aidres (int | None): 成功合成的小哥的 ID
            possibility (float | None): 成功率
        """
        aid1, aid2, aid3 = sorted([aid1, aid2, aid3])

        # 先检查有没有这个配方
        rec = await self.get_recipe(aid1, aid2, aid3)
        if not rec:
            # 检查，如果两个参数缺一个，就报错

            if aidres is None or possibility is None:
                raise RecipeMissing()
            await self.add_recipe(aid1, aid2, aid3, aidres, possibility, True)
            return

        aidres = aidres if aidres is not None else rec[0]
        possibility = possibility if possibility is not None else rec[1]

        query = (
            update(Recipe)
            .where(
                Recipe.award1 == aid1,
                Recipe.award2 == aid2,
                Recipe.award3 == aid3,
            )
            .values(
                aidres=aidres,
                possibility=possibility,
                modified=1,
            )
        )
        
        await self.session.execute(query)

    async def clear_not_modified(self) -> None:
        """删除所有未修改的配方"""
        query = delete(Recipe).where(Recipe.modified == 0)

        await self.session.execute(query)
        await self.session.flush()
