from src.base.command_events import OnebotContext
from src.base.exceptions import ObjectNotFoundException
from src.common.data.awards import get_award_info
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
)
from src.core.unit_of_work import get_unit_of_work
from arclet.alconna import Alconna, Arg, Arparma, Option


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        "re:(查配方|查询配方|查找配方|cpf|pf)",
        ["::"],
        Arg("name1", str),
        Arg("name2", str),
        Arg("name3", str),
    )
)
async def _(ctx: OnebotContext, res: Arparma):
    n1 = res.query[str]("name1")
    n2 = res.query[str]("name2")
    n3 = res.query[str]("name3")

    if n1 is None or n2 is None or n3 is None:
        return

    async with get_unit_of_work() as uow:
        a1 = await uow.awards.get_aid_strong(n1)
        a2 = await uow.awards.get_aid_strong(n2)
        a3 = await uow.awards.get_aid_strong(n3)

        re = await uow.recipes.get_recipe(a1, a2, a3)
        if re is None:
            raise ObjectNotFoundException("配方", f"{n1} + {n2} + {n3}")

        info = await get_award_info(uow, re[0])

        await ctx.reply(f"{n1}+{n2}+{n3} 合成 {info.name}，概率为 {re[1]*100}%")


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        "re:(更改|改变|设置|调整|添加|新增|增加)(合成)?配方",
        ["::"],
        Arg("name1", str),
        Arg("name2", str),
        Arg("name3", str),
        Option(
            "--result",
            Arg("name4", str),
            alias=["-r", "结果", "成品", "收获"],
        ),
        Option(
            "--possibility",
            Arg("posi", float),
            alias=["-p", "概率", "频率", "收获率", "合成率", "成功率"],
        ),
    )
)
async def _(ctx: OnebotContext, res: Arparma):
    n1 = res.query[str]("name1")
    n2 = res.query[str]("name2")
    n3 = res.query[str]("name3")

    if n1 is None or n2 is None or n3 is None:
        return

    async with get_unit_of_work() as uow:
        a1 = await uow.awards.get_aid_strong(n1)
        a2 = await uow.awards.get_aid_strong(n2)
        a3 = await uow.awards.get_aid_strong(n3)

        n4 = res.query[str]("name4")
        a4 = None if n4 is None else await uow.awards.get_aid_strong(n4)
        po = res.query[float]("posi")

        await uow.recipes.update_recipe(a1, a2, a3, a4, po)

    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "删除所有配方",
        Option("--force", alias=["-f", "强制"]),
    )
)
async def _(ctx: OnebotContext, res: Arparma):
    async with get_unit_of_work() as uow:
        await uow.recipes.clear_not_modified(force=res.exist("--force"))
    await ctx.reply("ok.")
