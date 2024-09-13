from arclet.alconna import Alconna, Arg, Arparma
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import GroupContext
from src.base.event.event_root import throw_event
from src.common.command_deco import (
    limited,
    listen_message,
    match_alconna,
    require_awake,
)
from src.common.data.awards import generate_random_info, get_award_info, use_award
from src.common.data.recipe import try_merge
from src.common.data.user import get_user_data
from src.common.dataclasses.game_events import MergeEvent
from src.common.rd import get_random
from src.core.unit_of_work import get_unit_of_work
from src.logic.catch import handle_baibianxiaoge
from src.services.stats import StatService
from src.ui.base.browser import get_render_pool
from src.ui.types.common import GetAward
from src.ui.types.recipe import MergeData, MergeMeta


@listen_message()
@limited
@match_alconna(
    Alconna(
        "re:(合成|hc)(小哥|xg)?",
        Arg(
            "第一个小哥", str
        ),  # 因为参数丢失的时候可能会显示名字，所以这里我改成了中文。
        Arg("第二个小哥", str),
        Arg("第三个小哥", str),
    )
)
@require_awake
async def _(ctx: GroupContext, res: Arparma):
    costs = {0: 20, 1: 3, 2: 8, 3: 12, 4: 15, 5: 17}

    n1 = res.query[str]("第一个小哥")
    n2 = res.query[str]("第二个小哥")
    n3 = res.query[str]("第三个小哥")
    if n1 is None or n2 is None or n3 is None:
        return

    async with get_unit_of_work(qqid=ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)

        if not await uow.user_flag.have(uid, "合成"):
            await ctx.reply("你没有买小哥合成凭证，被门口的保安拦住了。")
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

        after = await uow.money.use(uid, cost)

        aid, succeed = await try_merge(uow, uid, a1, a2, a3)
        rid = await uow.recipes.get_recipe_id(a1, a2, a3)
        stid1, stid2 = await StatService(uow).hc(uid, rid, succeed, aid, cost)
        if aid == -1:
            info = await generate_random_info()
            add = get_random().randint(1, 100)
            data = GetAward(
                info=info,
                count=add,
                is_new=False,
            )
        else:
            info = await get_award_info(uow, aid, uid)
            add = get_random().randint(1, 3)
            data = GetAward(
                info=info,
                count=add,
                is_new=await uow.inventories.get_stats(uid, aid) == 0,
            )
            await uow.inventories.give(uid, aid, add)
            if aid == 35:
                await handle_baibianxiaoge(uow, uid)

        if succeed:
            status = "成功！"
        elif aid in (89, -1):
            status = "失败！"
        else:
            status = "失败？"

        user = await get_user_data(ctx, uow)
        merge_info = MergeData(
            user=user,
            meta=MergeMeta(
                recipe_id=rid,
                stat_id=stid1,
                cost_chip=cost,
                own_chip=int(after),
                status=status,
                is_strange=status == "失败？",
            ),
            inputs=(info1, info2, info3),
            output=data,
        )

    await ctx.send(
        UniMessage.image(raw=await get_render_pool().render("recipe", merge_info))
    )
    await throw_event(MergeEvent(user_data=user, merge_view=merge_info))


@listen_message()
@match_alconna(
    Alconna(
        "re:(合成|hc)(档案|da)",
        Arg("产物小哥", str)
    )
)
async def _(ctx: GroupContext, res: Arparma):
    name = res.query[str]("产物小哥")
    if name == None:
        return
    
    async with get_unit_of_work(ctx.sender_id) as uow:
        aid = await uow.awards.get_aid_strong(name)
        recipe_ids = await uow.recipes.get_recipe_by_product(aid)
        message = "历史测试：\n"
        for recipe_id in recipe_ids:
            recipe = await uow.recipes.get_recipe_info(recipe_id)
            award1 = (await uow.awards.get_info(recipe.aid1)).name
            award2 = (await uow.awards.get_info(recipe.aid2)).name
            award3 = (await uow.awards.get_info(recipe.aid3)).name
            message += f"{award1} + {award2} + {award3} ({recipe.possibility})\n"
        await ctx.send(UniMessage.text(message))