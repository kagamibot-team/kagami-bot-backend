from sqlalchemy import delete, insert, select, update

from ..base.exceptions import ObjectAlreadyExistsException, RecipeMissingException
from ..base.repository import DBRepository
from ..models.models import Recipe


class RecipeRepository(DBRepository):
    """
    小哥合成配方的仓库
    """

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

    async def get_recipe_id(self, aid1: int, aid2: int, aid3: int) -> int:
        """获得某个合成配方的 ID

        Args:
            aid1 (int): 第一个小哥的 ID
            aid2 (int): 第二个小哥的 ID
            aid3 (int): 第三个小哥的 ID

        Returns:
            int: 合成配方的 ID
        """

        aid1, aid2, aid3 = sorted([aid1, aid2, aid3])

        query = select(Recipe.data_id).filter(
            Recipe.award1 == aid1, Recipe.award2 == aid2, Recipe.award3 == aid3
        )

        return (await self.session.execute(query)).scalar_one()

    async def add_recipe(
        self,
        aid1: int,
        aid2: int,
        aid3: int,
        aidres: int,
        possibility: float,
        modified: bool = False,
    ) -> None:
        """添加一个配方。当配方存在时，会抛出 `ObjectAlreadyExistsException` 异常。

        Args:
            aid1 (int): 第一个小哥的 ID
            aid2 (int): 第二个小哥的 ID
            aid3 (int): 第三个小哥的 ID
            aidres (int): 成功合成的小哥的 ID
            possibility (float): 成功率
        """
        aid1, aid2, aid3 = sorted([aid1, aid2, aid3])
        if await self.get_recipe(aid1, aid2, aid3) is not None:
            raise ObjectAlreadyExistsException(f"Recipe<{aid1}, {aid2}, {aid3}>")
        await self.session.execute(
            insert(Recipe).values(
                {
                    Recipe.award1: aid1,
                    Recipe.award2: aid2,
                    Recipe.award3: aid3,
                    Recipe.result: aidres,
                    Recipe.possibility: possibility,
                    Recipe.modified: 1 if modified else 0,
                }
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
                raise RecipeMissingException()
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
                {
                    Recipe.result: aidres,
                    Recipe.possibility: possibility,
                    Recipe.modified: 1,
                }
            )
        )

        await self.session.execute(query)

    async def clear_not_modified(self, force: bool = False) -> None:
        """删除所有未修改的配方"""
        query = delete(Recipe)
        if not force:
            query = query.where(Recipe.modified == 0)

        await self.session.execute(query)
        await self.session.flush()

    async def reset_recipe(self, aid1: int, aid2: int, aid3: int) -> None:
        """重置配方到初始状态，即删除这个配方"""

        aid1, aid2, aid3 = sorted([aid1, aid2, aid3])
        await self.session.execute(
            delete(Recipe).where(
                Recipe.award1 == aid1, Recipe.award2 == aid2, Recipe.award3 == aid3
            )
        )
        await self.session.flush()

    async def is_modified(self, aid1: int, aid2: int, aid3: int) -> bool:
        """检查一个配方是否被更改"""

        aid1, aid2, aid3 = sorted([aid1, aid2, aid3])

        query = select(Recipe.modified).filter(
            Recipe.award1 == aid1, Recipe.award2 == aid2, Recipe.award3 == aid3
        )

        return (await self.session.execute(query)).scalar_one_or_none() == 1

    async def get_all_special(self):
        """
        获取所有特殊配方

        返回的 tuple 顺序是三个输入 aid，一个输出 aid，一个概率
        """

        query = select(
            Recipe.award1,
            Recipe.award2,
            Recipe.award3,
            Recipe.result,
            Recipe.possibility,
        ).filter(Recipe.modified == 1)

        return list((await self.session.execute(query)).tuples().all())
