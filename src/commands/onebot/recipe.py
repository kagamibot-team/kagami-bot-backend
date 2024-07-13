from arclet.alconna import Alconna, Arg, Arparma

from interfaces.nonebot.views.recipe import render_merge_message
from src.base.command_events import GroupContext, OnebotMessageContext
from src.base.local_storage import Action, XBRecord, get_localdata
from src.common.data.awards import (
    generate_random_info,
    uow_get_award_info,
    uow_use_award,
)
from src.common.data.recipe import try_merge
from src.common.decorators.command_decorators import (
    kagami_exception_handler,
    listenOnebot,
    matchAlconna,
)
from src.common.rd import get_random
from src.common.times import now_datetime
from src.core.unit_of_work import get_unit_of_work
from src.views.recipe import MergeResult, MergeStatus


@listenOnebot()
@kagami_exception_handler()
@matchAlconna(
    Alconna(
        "re:(合成|hc)(小哥|xg)?",
        Arg("name1", str),
        Arg("name2", str),
        Arg("name3", str),
    )
)
async def _(ctx: OnebotMessageContext, res: Arparma):
    costs = {0: 20, 1: 3, 2: 8, 3: 12, 4: 15, 5: 17}

    n1 = res.query[str]("name1")
    n2 = res.query[str]("name2")
    n3 = res.query[str]("name3")
    if n1 is None or n2 is None or n3 is None:
        return

    username = await ctx.getSenderName()

    async with get_unit_of_work(qqid=ctx.getSenderId()) as uow:
        uid = await uow.users.get_uid(ctx.getSenderId())

        if not await uow.users.do_have_flag(uid, "合成"):
            await ctx.reply("先去小镜商店买了机器使用凭证，你才能碰这台机器。")
            return

        a1 = await uow.awards.get_aid_strong(n1)
        a2 = await uow.awards.get_aid_strong(n2)
        a3 = await uow.awards.get_aid_strong(n3)
        info1 = await uow_get_award_info(uow, a1)
        info2 = await uow_get_award_info(uow, a2)
        info3 = await uow_get_award_info(uow, a3)
        cost = costs[info1.level.lid] + costs[info2.level.lid] + costs[info3.level.lid]

        using: dict[int, int] = {}
        for aid in (a1, a2, a3):
            using.setdefault(aid, 0)
            using[aid] += 1
        for aid, use in using.items():
            await uow_use_award(uow, uid, aid, use)

        after = await uow.users.use_money(uid, cost)

        aid, succeed = await try_merge(uow.session, uid, a1, a2, a3)
        if aid == -1:
            info = await generate_random_info()
            add = get_random().randint(1, 100)
            do_xb = False
            info.notation = f"+{add}"
        else:
            info = await uow_get_award_info(uow, aid, uid)
            add = get_random().randint(1, 3)
            do_xb = info.level.lid in (4, 5)
            info.notation = f"+{add}"
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
            username=username,
            successed=status,
            inputs=(info1, info2, info3),
            output=info,
            cost_money=cost,
            remain_money=int(after),
        )

    await ctx.send(await render_merge_message(merge_info))

    if isinstance(ctx, GroupContext) and do_xb:
        get_localdata().add_xb(
            ctx.event.group_id,
            ctx.getSenderId(),
            XBRecord(
                time=now_datetime(), action=Action.merged, data=f"{info.name} ×{add}"
            ),
        )
