from arclet.alconna import Alconna, Arg, Arparma, Option
from loguru import logger

from src.base.command_events import MessageContext
from src.base.exceptions import ObjectNotFoundException
from src.common.command_deco import (
    listen_message,
    match_alconna,
    match_literal,
    require_admin,
)
from src.common.data.awards import get_award_info
from src.common.data.recipe import calc_possibility
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
            raise ObjectNotFoundException("配方")

        info = await get_award_info(uow, re[0])
        modified = await uow.recipes.is_modified(a1, a2, a3)

        await ctx.reply(
            f"{n1}+{n2}+{n3} 合成 {info.name}，概率为 {re[1]*100}%，modified={modified}"
        )


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "re:(算概率)",
        ["::"],
        Arg("name1", int),
        Arg("name2", int),
        Arg("name3", int),
        Arg("namer", int),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    lid1 = res.query[int]("name1", 0)
    lid2 = res.query[int]("name2", 0)
    lid3 = res.query[int]("name3", 0)
    lidr = res.query[int]("namer", 0)

    if (
        lid1 < 0
        or lid2 < 0
        or lid3 < 0
        or lidr < 0
        or lid1 > 5
        or lid2 > 5
        or lid3 > 5
        or lidr > 5
    ):
        raise ValueError("等级错误")

    poss = calc_possibility(lid1, lid2, lid3, lidr)

    await ctx.reply(f"{lid1}+{lid2}+{lid3} -> {lidr}，概率为 {poss*100}%。")


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
            Arg("namer", str),
            alias=["-r", "结果", "成品", "收获"],
        ),
        Option(
            "--possibility",
            Arg("posi", float),
            alias=["-p", "概率", "频率", "收获率", "合成率", "成功率"],
        ),
        Option(
            "--special",
            Arg(
                "mode", str
            ),  # up：设定为以原概率为基础提升的固定概率；reset：保留合理产物，重置配方的概率与is_modified内容
            alias=["-s", "特殊"],
        ),
        Option("--clear", alias=["清除"]),  # 完全清空配方，回到不存在此条配方的状态
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

        if res.exist("clear"):
            await uow.recipes.reset_recipe(a1, a2, a3)
            await ctx.reply("ok.\n已清除配方。")
            return

        # 获取配方信息
        rid = await uow.recipes.get_recipe_id(a1, a2, a3)
        if rid is not None:
            rinfo = await uow.recipes.get_recipe_info(rid)
        else:
            rinfo = None

        # 获取产物信息，若留空则取配方目前产物，若配方不存在则报错
        nr = res.query[str]("namer")
        if nr is not None:
            ar = await uow.awards.get_aid_strong(nr)
        else:
            if rid is None or rinfo is None:
                raise ObjectNotFoundException("配方")
            ar = rinfo.result
            nr = (await uow.awards.get_info(ar)).name

        # 获取概率信息，若留空则取配方目前概率，若配方不存在则报错
        po = res.query[float]("posi")
        if po is None:
            if rid is None or rinfo is None:
                raise ObjectNotFoundException("配方")
            po = rinfo.possibility

        # 默认标记为特殊配方
        mod = 1

        if res.exist("special"):
            mode = res.query[str]("mode")

            lid1 = await uow.awards.get_lid(a1)
            lid2 = await uow.awards.get_lid(a2)
            lid3 = await uow.awards.get_lid(a3)
            lidr = await uow.awards.get_lid(ar)

            # reset模式下产物需要满足正常配方的要求
            if mode == "reset":
                if lidr == 0 or max(lid1, lid2, lid3) - 1 > lidr:
                    raise ValueError("产物等级错误")

                pid1 = await uow.pack.get_main_pack(a1)
                pid2 = await uow.pack.get_main_pack(a2)
                pid3 = await uow.pack.get_main_pack(a3)
                pidr = await uow.pack.get_main_pack(ar)
                if pidr > 0 and pid1 != pidr and pid2 != pidr and pid3 != pidr:
                    raise ValueError("产物猎场错误")

            poss = calc_possibility(lid1, lid2, lid3, lidr)
            # up模式下设定为以原概率为基础提升的固定概率
            if mode == "up":
                po = 1 - (1 - poss) ** 2
            # reset模式下还原概率，并标记为普通配方
            if mode == "reset":
                po = poss
                mod = 0

        await uow.recipes.update_recipe(a1, a2, a3, ar, po, mod)

        await ctx.reply(
            f"ok.\n结果为：{n1} {n2} {n3} -> {nr}，概率为 {po*100}%，modified={mod}"
        )


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
                f"{info1.name} {info2.name} {info3.name} -> {info.name}，"
                f"概率为 {posi*100}%"
            )

    await ctx.send("所有的特殊配方：\n" + "\n".join(msg))


@listen_message()
@require_admin()
@match_alconna(Alconna(["::"], "re:(所有配方)", Arg("产物小哥", str)))
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("产物小哥")
    if name == None:
        return
    msg = ""

    async with get_unit_of_work(ctx.sender_id) as uow:
        aid = await uow.awards.get_aid_strong(name)

        if await uow.pack.get_main_pack(aid) != -1:
            recipe_ids = await uow.stats.get_merge_by_product(
                aid
            )  # [0]是stat_id，[1]是recipe_id，[2]是update_at
        else:
            recipe_ids = []
        seen: set[int] = set()  # 去重
        for recipe_id in recipe_ids:
            if recipe_id[1] not in seen:
                recipe = await uow.recipes.get_recipe_info(recipe_id[1])
                if recipe is None:
                    raise ObjectNotFoundException("配方")

                n1 = (await uow.awards.get_info(recipe.aid1)).name
                n2 = (await uow.awards.get_info(recipe.aid2)).name
                n3 = (await uow.awards.get_info(recipe.aid3)).name

                msg += f"{n1} {n2} {n3}\n"
                seen.add(recipe_id[1])

    await ctx.send(f"{ name }的所有配方：\n" + "".join(msg))


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(test_zero)",
    )
)
async def _(ctx: MessageContext, _: Arparma):
    async with get_unit_of_work() as uow:
        msg = "所有通用小哥配方：\n"
        for i in range(1, 20713):
            info = await uow.recipes.get_recipe_info(i)
            if info is None:
                continue
            if (await uow.awards.get_info(info.aid1)).level.lid == 0:
                continue
            if (await uow.awards.get_info(info.aid2)).level.lid == 0:
                continue
            if (await uow.awards.get_info(info.aid3)).level.lid == 0:
                continue
            if await uow.pack.get_main_pack(info.aid1) > 0:
                continue
            if await uow.pack.get_main_pack(info.aid2) > 0:
                continue
            if await uow.pack.get_main_pack(info.aid3) > 0:
                continue

            logger.info(f"{i} 号准备就绪")
            n1 = (await uow.awards.get_info(info.aid1)).name
            n2 = (await uow.awards.get_info(info.aid2)).name
            n3 = (await uow.awards.get_info(info.aid3)).name
            nr = (await uow.awards.get_info(info.result)).name
            msg += f"{i}: {n1} {n2} {n3} -> {nr}\n"
    
        await ctx.send(msg)