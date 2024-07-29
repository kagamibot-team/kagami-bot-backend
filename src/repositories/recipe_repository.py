from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Award
from src.models.recipe_history import RecipeHistory
from src.models.level import Level

from ..base.exceptions import ObjectAlreadyExistsException, RecipeMissingException
from ..base.repository import DBRepository
from ..models import Recipe


class RecipeRepository(DBRepository[Recipe]):
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
        await self.clear_history(await self.get_recipe_id(aid1, aid2, aid3))

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

    async def clear_history(self, rid: int):
        """清除某个合成配方所有的合成历史

        Args:
            rid (int): 配方的 ID
        """

        await self.session.execute(
            delete(RecipeHistory).where(RecipeHistory.recipe == rid)
        )

    async def limit_one_history(self, group_id: int | str, rid: int):
        """限制数据库中的合成历史只保留最旧的一个

        Args:
            group_id (int | str): 群 ID
            rid (int): 配方的 ID

        Returns:
            int | None: 如果有历史，返回最旧的历史的发现者 UID，否则返回 None
        """

        the_true_first_uid = await self.session.scalar(
            select(RecipeHistory.first)
            .where(
                RecipeHistory.source == str(group_id),
                RecipeHistory.recipe == rid,
            )
            .order_by(-RecipeHistory.data_id)
            .limit(1)
        )

        await self.session.execute(
            delete(RecipeHistory).where(
                RecipeHistory.source == str(group_id),
                RecipeHistory.recipe == rid,
            )
        )

        if the_true_first_uid is not None:
            await self.session.execute(
                insert(RecipeHistory).values(
                    {
                        RecipeHistory.source: str(group_id),
                        RecipeHistory.recipe: rid,
                        RecipeHistory.first: the_true_first_uid,
                    }
                )
            )

        return the_true_first_uid

    async def record_history(self, group_id: int | str, rid: int, uid: int):
        """记录下一次合成历史

        Args:
            group_id (int | str): 群 ID
            rid (int): 配方的 ID
            uid (int): 用户的 ID
        """

        # 前面忘记筛选了，这里只能人工再修复一下
        first = await self.limit_one_history(group_id, rid)

        if first is None:
            await self.session.execute(
                insert(RecipeHistory).values(
                    {
                        RecipeHistory.source: str(group_id),
                        RecipeHistory.recipe: rid,
                        RecipeHistory.first: uid,
                    }
                )
            )

    async def get_histories(
        self,
        group_id: int | str,
        result: int | None = None,
        level: int | Level | None = None,
        page_index: int = 0,
        page_size: int = 10,
    ):
        """获得抓小哥的历史记录合集

        Args:
            group_id (int | str): 群 ID
            result (int | None, optional): 筛选条件之合成出来的小哥 ID. Defaults to None.
            level (int | Level | None, optional): 筛选条件之等级. Defaults to None.
            page_index (int, optional): 第几页（程序的方式定义索引）. Defaults to 0.
            page_size (int, optional): 一页多少个. Defaults to 10.

        Returns:
            Sequence[tuple[int, int, int, int, int, datetime]]: 输入的三个 ID，输出的一个 ID，第一个发现者的 UID，记录的时间
        """

        query = (
            select(
                Recipe.award1,
                Recipe.award2,
                Recipe.award3,
                Recipe.result,
                RecipeHistory.first,
                RecipeHistory.created_at,
            )
            .join(RecipeHistory, RecipeHistory.recipe == Recipe.data_id)
            .filter(RecipeHistory.source == str(group_id))
        )

        if result is not None:
            query = query.filter(Recipe.result == result)

        if level is not None:
            if isinstance(level, Level):
                level = level.lid
            query = query.join(Award, Recipe.result == Award.data_id)
            query = query.filter(Award.level_id == level)

        query = query.order_by(-RecipeHistory.data_id)
        query = query.offset(page_index * page_size)
        query = query.limit(page_size)

        return (await self.session.execute(query)).tuples().all()
