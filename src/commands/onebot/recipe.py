from src.base.local_storage import Action, XBRecord, get_localdata
from src.common.decorators.command_decorators import kagami_exception_handler
from src.common.rd import get_random
from src.core.unit_of_work import UnitOfWork
from src.imports import *


async def _get_lid(session: AsyncSession, a: int):
    return (
        await session.execute(select(Award.level_id).filter(Award.data_id == a))
    ).scalar_one()


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

    async with UnitOfWork(DatabaseManager.get_single()) as uow:
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
        else:
            info = await uow_get_award_info(uow, aid, uid)
            add = get_random().randint(1, 3)
            do_xb = info.level.lid in (4, 5)
            await uow.inventories.give(uid, aid, add)

    username = await ctx.getSenderName()
    if isinstance(ctx, GroupContext):
        username = await ctx.getSenderName()

    area_title_1 = await getTextImage(
        text=f"{username} 的合成材料：",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=80,
        margin_bottom=30,
    )

    box1 = await display_box(info1.level.color, info1.image, False)
    box2 = await display_box(info2.level.color, info2.image, False)
    box3 = await display_box(info3.level.color, info3.image, False)
    area_material_box = await pileImages(
        images=[box1, box2, box3],
        background="#8A8580",
        paddingX=24,
        marginLeft=18,
        marginBottom=24,
    )

    succeeded = "成功" if succeed else "失败"
    succeeded_sign = "！" if succeed or aid == 89 or aid == -1 else "？"

    area_title_2 = await getTextImage(
        text=f"合成结果：{succeeded}{succeeded_sign}",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=60,
        margin_bottom=18,
    )

    area_product_entry = await catch(
        title=info.name,
        description=info.description,
        image=info.image,
        stars=info.level.display_name,
        color=info.level.color,
        new=info.new,
        notation=f"+{add}",
    )

    area_title_3 = await getTextImage(
        text=f"本次合成花费了你 {cost} 薯片，你还有 {after} 薯片。",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=24,
        margin_top=12,
    )

    img = await verticalPile(
        [
            area_title_1,
            area_material_box,
            area_title_2,
            area_product_entry,
            area_title_3,
        ],
        15,
        "left",
        "#8A8580",
        60,
        60,
        60,
        60,
    )
    await ctx.send(UniMessage.image(raw=imageToBytes(img)))

    if isinstance(ctx, GroupContext) and do_xb:
        get_localdata().add_xb(
            ctx.event.group_id,
            ctx.getSenderId(),
            XBRecord(
                time=now_datetime(), action=Action.merged, data=f"{info.name} ×{add}"
            ),
        )
