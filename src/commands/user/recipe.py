from arclet.alconna import Alconna, Arg, Arparma
from nonebot_plugin_alconna import UniMessage

from loguru import logger
from src.base.command_events import GroupContext
from src.base.exceptions import ObjectNotFoundException
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
from src.ui.base.render import get_render_pool
from src.ui.types.common import GetAward, AwardInfo
from src.ui.types.recipe import MergeData, MergeMeta, RecipeArchiveData
from src.ui.types.recipe import RecipeInfo


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
        aft_sto1 = await uow.inventories.get_storage(uid, a1)
        aft_sto2 = await uow.inventories.get_storage(uid, a2)
        aft_sto3 = await uow.inventories.get_storage(uid, a3)

        aid, succeed = await try_merge(uow, uid, a1, a2, a3)
        rid = await uow.recipes.get_recipe_id(a1, a2, a3)
        if rid is None:
            raise ObjectNotFoundException("配方")
        stid1, stid2 = await StatService(uow).hc(uid, rid, succeed, aid, cost)
        if aid == -1:
            info = await generate_random_info()
            add = get_random().randint(1, 100)
            data = GetAward(
                info=info,
                count=add,
                is_new=False,
            )
            aft_stor = 0
        else:
            if aid == 35:
                stats = await uow.inventories.get_stats(uid, aid)
                if stats > 0:
                    await handle_baibianxiaoge(uow, uid)
            info = await get_award_info(uow, aid, uid)
            add = get_random().randint(1, 3)
            data = GetAward(
                info=info,
                count=add,
                is_new=await uow.inventories.get_stats(uid, aid) == 0,
            )
            await uow.inventories.give(uid, aid, add)
            aft_stor = await uow.inventories.get_storage(uid, aid)

        if succeed:
            status = "成功！"
        elif aid in (89, -1):
            status = "失败！"
        else:
            status = "失败？"

        user = await get_user_data(ctx, uow)
        merge_info = MergeData(
            inputs=(info1, info2, info3),
            after_storages=(aft_sto1, aft_sto2, aft_sto3, aft_stor),
            light_off=(True, True, True, True),
            possibility=1,
            output=data,
            recipe_id=rid,
            stat_id=stid1,
            meta=MergeMeta(
                user=user,
                cost_chip=cost,
                own_chip=int(after),
                status=status,
                is_strange=status == "失败？",
            ),
        )

    await ctx.send(
        UniMessage.image(raw=await get_render_pool().render("recipe", merge_info))
    )
    await throw_event(MergeEvent(user_data=user, merge_view=merge_info))


@listen_message()
@limited
@match_alconna(
    Alconna(
        "re:(合成|hc)(档案|da)",
        Arg("产物小哥", str)
    )
)
@require_awake
async def _(ctx: GroupContext, res: Arparma):
    costs = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32}

    name = res.query[str]("产物小哥")
    if name == None:
        return
    
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)

        if not await uow.user_flag.have(uid, "合成"):
            await ctx.reply("你没有买小哥合成凭证，被门口的保安拦住了。")
            return
        
        aid = await uow.awards.get_aid_strong(name)
        product = await uow.awards.get_info(aid)
        after = await uow.money.use(uid, costs[product.level.lid])

        stat = await uow.inventories.get_stats(uid, aid)
        if stat == 0: #没见过
            product.image_name = "blank_placeholder.png"
            product.color = "#696361"

        if await uow.pack.get_main_pack(aid) != -1:
            recipe_ids = await uow.stats.get_merge_by_product(aid)  # [0]是stat_id，[1]是recipe_id，[2]是update_at
        else: recipe_ids = []
        unique_recipes: list[list[RecipeInfo]] = [[], [], [], []]
        seen: set[int] = set() # 去重
        for recipe_id in recipe_ids:
            if recipe_id[1] not in seen:
                recipe = await uow.recipes.get_recipe_info(recipe_id[1])
                if recipe is None:
                    raise ObjectNotFoundException("配方")
                recipe.stat_id = recipe_id[0]
                recipe.updated_at = recipe_id[2]

                n1 = (await uow.awards.get_info(recipe.aid1)).name
                sto1 = await uow.inventories.get_storage(uid, recipe.aid1)
                sto2 = await uow.inventories.get_storage(uid, recipe.aid2)
                sto3 = await uow.inventories.get_storage(uid, recipe.aid3)

                if recipe.aid1 == recipe.aid2 and recipe.aid2 == recipe.aid3:
                    cnt = sto1 if sto1 < 3 else 3
                elif recipe.aid1 == recipe.aid2 and recipe.aid2 != recipe.aid3:
                    cnt = (sto1 if sto1 < 2 else 2) + (sto3 if sto3 < 1 else 1)
                elif recipe.aid1 != recipe.aid2 and recipe.aid2 == recipe.aid3:
                    cnt = (sto1 if sto1 < 1 else 1) + (sto2 if sto2 < 2 else 2)
                else:
                    cnt = (sto1 if sto1 < 1 else 1) + (sto2 if sto2 < 1 else 1)+ (sto3 if sto3 < 1 else 1)
                
                logger.info(f"{n1} {sto1} {sto2} {sto3} cnt {cnt}")

                unique_recipes[cnt].append(recipe)
                seen.add(recipe_id[1])

        recipes: list[RecipeInfo] = []
        recipes_display: list[MergeData] = []
        good_enough = False
        for i in range(3, -1, -1):
            for recipe in unique_recipes[i]:
                if i == 3: good_enough = True
                recipes.append(recipe)
        for i in range(3):
            stor = await uow.inventories.get_storage(uid, product.aid)

            if i < len(recipes):
                recipe = recipes[i]

                award1 = await uow.awards.get_info(recipe.aid1)
                award2 = await uow.awards.get_info(recipe.aid2)
                award3 = await uow.awards.get_info(recipe.aid3)
                sto1 = await uow.inventories.get_storage(uid, recipe.aid1)
                sto2 = await uow.inventories.get_storage(uid, recipe.aid2)
                sto3 = await uow.inventories.get_storage(uid, recipe.aid3)

                if recipe.aid1 == recipe.aid2 and recipe.aid2 == recipe.aid3:
                    off1 = (sto1 < 1); off2 = (sto2 < 2); off3 = (sto3 < 3)
                elif recipe.aid1 == recipe.aid2 and recipe.aid2 != recipe.aid3:
                    off1 = (sto1 < 1); off2 = (sto2 < 2); off3 = (sto3 < 1)
                elif recipe.aid1 != recipe.aid2 and recipe.aid2 == recipe.aid3:
                    off1 = (sto1 < 1); off2 = (sto2 < 1); off3 = (sto3 < 2)
                else:
                    off1 = (sto1 < 1); off2 = (sto2 < 1); off3 = (sto3 < 1)
        
                stat = await uow.inventories.get_stats(uid, recipe.aid1)
                if stat == 0: #没见过
                    award1.image_name = "blank_placeholder.png"
                    award1.color = "#696361"
                stat = await uow.inventories.get_stats(uid, recipe.aid2)
                if stat == 0: #没见过
                    award2.image_name = "blank_placeholder.png"
                    award2.color = "#696361"
                stat = await uow.inventories.get_stats(uid, recipe.aid3)
                if stat == 0: #没见过
                    award3.image_name = "blank_placeholder.png"
                    award3.color = "#696361"

                recipes_display.append(
                    MergeData(
                        inputs=(award1, award2, award3),
                        after_storages=(sto1, sto2, sto3, stor),
                        light_off=(off1, off2, off3, stor < 1),
                        possibility=recipe.possibility,
                        output=GetAward(
                            info=product,
                            count=0,
                            is_new=False,
                        ),
                        recipe_id=recipes[i].recipe_id,
                        stat_id=recipes[i].stat_id,
                        last_time=recipe.updated_at.strftime("%m月%d日%H时%M分")
                    )
                )
            else:
                award = AwardInfo()
                recipes_display.append(
                    MergeData(
                        inputs=(award, award, award),
                        after_storages=(0, 0, 0, stor),
                        light_off=(True, True, True, stor < 1),
                        possibility=-1,
                        output=GetAward(
                            info=product,
                            count=0,
                            is_new=False,
                        ),
                        recipe_id=0,
                        stat_id=0,
                    )
                )
        
        user = await get_user_data(ctx, uow)
        archive_info=RecipeArchiveData(
            user=user,
            recipes=recipes_display,
            product=product,
            cost_chip=costs[product.level.lid],
            own_chip=int(after),
            good_enough=good_enough
        )

    await ctx.send(
        UniMessage.image(raw=await get_render_pool().render("recipe_archive", archive_info))
    )