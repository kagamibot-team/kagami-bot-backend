import functools
from random import Random

from arclet.alconna import Alconna, Arg, Arparma
from loguru import logger
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import GroupContext
from src.base.event.event_root import throw_event
from src.base.exceptions import ObjectNotFoundException
from src.base.res import blank_placeholder
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
from src.common.dialogue import DialogFrom, get_dialog
from src.common.global_flags import global_flags
from src.common.rd import get_random
from src.core.unit_of_work import get_unit_of_work
from src.logic.catch import handle_baibianxiaoge
from src.models.level import level_repo
from src.services.stats import StatService
from src.ui.base.render import get_render_pool
from src.ui.types.common import AwardInfo, GetAward
from src.ui.types.recipe import MergeData, MergeMeta, RecipeArchiveData, RecipeInfo


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

        a1, a2, a3 = await uow.awards.get_aids_strong(n1, n2, n3)
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

        after = await uow.chips.use(uid, cost)
        aft_sto1 = await uow.inventories.get_storage(uid, a1)
        aft_sto2 = await uow.inventories.get_storage(uid, a2)
        aft_sto3 = await uow.inventories.get_storage(uid, a3)

        aid, succeed = await try_merge(uow, uid, a1, a2, a3)
        rid = await uow.recipes.get_recipe_id(a1, a2, a3)
        assert rid is not None, "配方在数据库中丢失"
        stid1, _ = await StatService(uow).hc(uid, rid, succeed, aid, cost)

        if aid == -1:
            # 乱码小哥，丢失
            info = await generate_random_info(uow)
            add = get_random().randint(1, 100)
            data = GetAward(info=info, count=add, is_new=False)
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

        status = "成功！" if succeed else ("失败！" if aid in (89, -1) else "失败？")
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
        bind_dialog(merge_info)

    await ctx.send_image(await get_render_pool().render("recipe", merge_info))
    await throw_event(MergeEvent(user_data=user, merge_view=merge_info))


def is_strange(data: MergeData) -> bool:
    return functools.reduce(
        lambda x, y: x or y,
        map(
            lambda info: info.level.lid == 0 and info.aid != 89,
            (*data.inputs, data.output.info),
        ),
    )


def bind_dialog(
    data: MergeData, hua_out: bool | None = None, random: Random | None = None
) -> None:
    if hua_out is None:
        with global_flags() as gf:
            hua_out = gf.activity_hua_out

    if random is None:
        random = get_random()

    flags: set[str]
    if not hua_out:
        dialog_from = DialogFrom.hecheng_normal
        if random.random() < 0.3:
            if is_strange(data):
                flags = set(("aqu_zero",))
            elif (oaid := data.output.info.aid) in (9, 34, 75, 98):
                flags = set((f"aqu_out{oaid}",))
            else:
                flags = set((f"aqu_outlv{data.output.info.level.lid}",))
        elif (oaid := data.output.info.aid) in (9, 34, 98, 516):
            flags = set((f"out{oaid}",))
        elif is_strange(data):
            flags = set(("zero",))
        else:
            lvin = max(map(lambda info: info.level.lid, data.inputs))
            flags = set((f"lv{lvin}_lv{data.output.info.level.lid}",))
    else:
        dialog_from = DialogFrom.hecheng_huaout
        if is_strange(data):
            flags = set(("zero",))
        elif (oaid := data.output.info.aid) in (9, 34, 75, 98):
            flags = set((f"out{oaid}",))
        else:
            flags = set((f"outlv{data.output.info.level.lid}",))

    data.dialog = random.choice(get_dialog(dialog_from, flags))


@listen_message()
@limited
@match_alconna(Alconna("re:(合成|hc)(档案|da)", Arg("产物小哥", str)))
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
        after = await uow.chips.use(uid, costs[product.level.lid])

        stat = await uow.inventories.get_stats(uid, aid)
        if stat == 0:  # 没见过
            product._img_resource = blank_placeholder()
            product.level = level_repo.get_by_id(0).to_data()

        if await uow.pack.get_main_pack(aid) != -1:
            recipe_ids = await uow.stats.get_merge_by_product(
                aid
            )  # [0]是stat_id，[1]是recipe_id，[2]是update_at
        else:
            recipe_ids = []
        unique_recipes: list[list[RecipeInfo]] = [[], [], [], []]
        seen: set[int] = set()  # 去重
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
                    cnt = (
                        (sto1 if sto1 < 1 else 1)
                        + (sto2 if sto2 < 1 else 1)
                        + (sto3 if sto3 < 1 else 1)
                    )

                logger.info(f"{n1} {sto1} {sto2} {sto3} cnt {cnt}")

                unique_recipes[cnt].append(recipe)
                seen.add(recipe_id[1])

        recipes: list[RecipeInfo] = []
        recipes_display: list[MergeData] = []
        good_enough = False
        for i in range(3, -1, -1):
            for recipe in unique_recipes[i]:
                if i == 3:
                    good_enough = True
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
                    off1 = sto1 < 1
                    off2 = sto2 < 2
                    off3 = sto3 < 3
                elif recipe.aid1 == recipe.aid2 and recipe.aid2 != recipe.aid3:
                    off1 = sto1 < 1
                    off2 = sto2 < 2
                    off3 = sto3 < 1
                elif recipe.aid1 != recipe.aid2 and recipe.aid2 == recipe.aid3:
                    off1 = sto1 < 1
                    off2 = sto2 < 1
                    off3 = sto3 < 2
                else:
                    off1 = sto1 < 1
                    off2 = sto2 < 1
                    off3 = sto3 < 1

                stat = await uow.inventories.get_stats(uid, recipe.aid1)
                if stat == 0:  # 没见过
                    award1._img_resource = blank_placeholder()
                    award1.level = level_repo.get_by_id(0).to_data()
                stat = await uow.inventories.get_stats(uid, recipe.aid2)
                if stat == 0:  # 没见过
                    award2._img_resource = blank_placeholder()
                    award2.level = level_repo.get_by_id(0).to_data()
                stat = await uow.inventories.get_stats(uid, recipe.aid3)
                if stat == 0:  # 没见过
                    award3._img_resource = blank_placeholder()
                    award3.level = level_repo.get_by_id(0).to_data()

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
                        last_time=recipe.updated_at.strftime("%m月%d日%H时%M分"),
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
        archive_info = RecipeArchiveData(
            user=user,
            recipes=recipes_display,
            product=product,
            cost_chip=costs[product.level.lid],
            own_chip=int(after),
            good_enough=good_enough,
        )

    await ctx.send_image(await get_render_pool().render("recipe_archive", archive_info))
