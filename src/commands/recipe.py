from arclet.alconna import Alconna, Arg, Arparma, Option

from src.base.command_events import GroupContext, OnebotContext
from src.base.exceptions import ObjectNotFoundException
from src.base.local_storage import Action, XBRecord, get_localdata
from src.common.data.awards import generate_random_info, get_award_info, use_award
from src.common.data.recipe import try_merge
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
)
from src.common.rd import get_random
from src.common.times import now_datetime
from src.core.unit_of_work import get_unit_of_work
from src.ui.pages.recipe import render_merge_message
from src.ui.views.award import GotAwardDisplay
from src.ui.views.recipe import MergeResult, MergeStatus
from src.ui.views.user import UserData


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


@listenOnebot()
@matchAlconna(
    Alconna(
        "re:(合成|hc)(小哥|xg)?",
        Arg("name1", str),
        Arg("name2", str),
        Arg("name3", str),
    )
)
async def _(ctx: OnebotContext, res: Arparma):
    costs = {0: 20, 1: 3, 2: 8, 3: 12, 4: 15, 5: 17}

    n1 = res.query[str]("name1")
    n2 = res.query[str]("name2")
    n3 = res.query[str]("name3")
    if n1 is None or n2 is None or n3 is None:
        return

    username = await ctx.get_sender_name()

    async with get_unit_of_work(qqid=ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)

        if not await uow.users.do_have_flag(uid, "合成"):
            await ctx.reply("先去小镜商店买了机器使用凭证，你才能碰这台机器。")
            return

        a1 = await uow.awards.get_aid_strong(n1)
        a2 = await uow.awards.get_aid_strong(n2)
        a3 = await uow.awards.get_aid_strong(n3)
        info1 = await get_award_info(uow, a1)
        info2 = await get_award_info(uow, a2)
        info3 = await get_award_info(uow, a3)
        cost = costs[info1.level.lid] + costs[info2.level.lid] + costs[info3.level.lid]

        using: dict[int, int] = {}
        for aid in (a1, a2, a3):
            using.setdefault(aid, 0)
            using[aid] += 1
        for aid, use in using.items():
            await use_award(uow, uid, aid, use)

        after = await uow.users.use_money(uid, cost)

        aid, succeed = await try_merge(uow.session, uid, a1, a2, a3)
        if aid == -1:
            info = await generate_random_info()
            add = get_random().randint(1, 100)
            do_xb = False
            data = GotAwardDisplay(info=info, count=add, is_new=False)
        else:
            info = await get_award_info(uow, aid, uid)
            add = get_random().randint(1, 3)
            do_xb = info.level.lid in (4, 5)
            data = GotAwardDisplay(info=info, count=add, is_new=await uow.inventories.get_stats(uid, aid) == 0)
            await uow.inventories.give(uid, aid, add)

        if isinstance(ctx, GroupContext):
            await uow.recipes.record_history(
                ctx.event.group_id,
                await uow.recipes.get_recipe_id(a1, a2, a3),
                uid,
            )

        if succeed:
            status = MergeStatus.success
        elif aid in (89, -1):
            status = MergeStatus.fail
        else:
            status = MergeStatus.what

        merge_info = MergeResult(
            user=UserData(
                uid=uid,
                qqid=str(ctx.sender_id),
                name=username,
            ),
            successed=status,
            inputs=(info1, info2, info3),
            output=data,
            cost_money=cost,
            remain_money=int(after),
        )

    await ctx.send(await render_merge_message(merge_info))

    if isinstance(ctx, GroupContext) and do_xb:
        get_localdata().add_xb(
            ctx.event.group_id,
            ctx.sender_id,
            XBRecord(
                time=now_datetime(), action=Action.merged, data=f"{info.name} ×{add}"
            ),
        )
