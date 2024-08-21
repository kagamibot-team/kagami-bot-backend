from arclet.alconna import Alconna, Arg, Arparma, Option

from src.base.command_events import MessageContext
from src.base.exceptions import ObjectNotFoundException
from src.common.data.awards import get_award_info
from src.common.command_deco import (
    listen_message,
    match_alconna,
    match_literal,
    require_admin,
)
from src.core.unit_of_work import get_unit_of_work


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "re:(查配方|查询配方|查找配方|cpf|pf)",
        ["::"],
        Arg("name1", str),
        Arg("name2", str),
        Arg("name3", str),
    )
)
async def _(ctx: MessageContext, res: Arparma):
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
        modified = await uow.recipes.is_modified(a1, a2, a3)

        await ctx.reply(
            f"{n1}+{n2}+{n3} 合成 {info.name}，概率为 {re[1]*100}%，modified={modified}"
        )


@listen_message()
@require_admin()
@match_alconna(
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
        Option("--reset", alias=["重置"]),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    n1 = res.query[str]("name1", "")
    n2 = res.query[str]("name2", "")
    n3 = res.query[str]("name3", "")

    async with get_unit_of_work() as uow:
        a1 = await uow.awards.get_aid_strong(n1)
        a2 = await uow.awards.get_aid_strong(n2)
        a3 = await uow.awards.get_aid_strong(n3)

        if res.exist("reset"):
            await uow.recipes.reset_recipe(a1, a2, a3)
            await ctx.reply("ok.")
            return

        n4 = res.query[str]("name4")
        a4 = None if n4 is None else await uow.awards.get_aid_strong(n4)
        po = res.query[float]("posi")

        await uow.recipes.update_recipe(a1, a2, a3, a4, po)

    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "删除所有配方",
        Option("--force", alias=["-f", "强制"]),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    async with get_unit_of_work() as uow:
        await uow.recipes.clear_not_modified(force=res.exist("--force"))
    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_literal("::所有特殊配方")
async def _(ctx: MessageContext):
    async with get_unit_of_work() as uow:
        msg: list[str] = []
        for aid1, aid2, aid3, aid, posi in await uow.recipes.get_all_special():
            info1 = await get_award_info(uow, aid1)
            info2 = await get_award_info(uow, aid2)
            info3 = await get_award_info(uow, aid3)
            info = await get_award_info(uow, aid)
            msg.append(
                f"{info1.name}+{info2.name}+{info3.name} 合成 {info.name}，"
                f"概率为 {posi*100}%"
            )

    await ctx.send("所有的特殊配方：\n" + "\n".join(msg))
