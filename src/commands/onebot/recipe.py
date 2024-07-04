from src.common.draw.strange import make_strange
from src.imports import *


@listenOnebot()
@matchAlconna(
    Alconna(
        "re:(合成|hc)(小哥|xg)?",
        Arg("name1", str),
        Arg("name2", str),
        Arg("name3", str),
    )
)
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, res: Arparma):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    cost = 40

    if not await do_user_have_flag(session, uid, "合成"):
        await ctx.reply(f"先去小镜商店买了机器使用凭证，你才能碰这台机器。")
        return

    n1 = res.query[str]("name1")
    n2 = res.query[str]("name2")
    n3 = res.query[str]("name3")

    if n1 is None or n2 is None or n3 is None:
        return

    a1 = await get_aid_by_name(session, n1)
    a2 = await get_aid_by_name(session, n2)
    a3 = await get_aid_by_name(session, n3)

    if a1 is None:
        await ctx.reply(f"啊啊——{n1} 是什么小哥？")
        return

    if a2 is None:
        await ctx.reply(f"啊啊——{n2} 是什么小哥？")
        return

    if a3 is None:
        await ctx.reply(f"啊啊——{n3} 是什么小哥？")
        return

    using: dict[int, int] = {}

    for aid in (a1, a2, a3):
        if aid in using.keys():
            using[aid] += 1
        else:
            using[aid] = 1

    for aid, v in using.items():
        st = await get_storage(session, uid, aid) or 0
        logger.info(f"{aid} {st} {v}")

        if st < v:
            if aid == a1:
                await ctx.reply(f"啊啊——麻烦先检查一下你的 {n1} 数量够不够吧")
            elif aid == a2:
                await ctx.reply(f"啊啊——麻烦先检查一下你的 {n2} 数量够不够吧")
            else:
                await ctx.reply(f"啊啊——麻烦先检查一下你的 {n3} 数量够不够吧")
            return

    for aid, v in using.items():
        await add_storage(session, uid, aid, -v)

    m = await get_user_money(session, uid)
    if m < cost:
        await ctx.reply(f"合成一次小哥要花 {cost} 薯片，你的薯片不够了哟")
        return
    await set_user_money(session, uid, m - cost)

    aid, succeed = await try_merge(session, uid, a1, a2, a3)

    if aid == -1:
        rlen = random.randint(2, 4)
        rlen2 = random.randint(30, 90)
        rchar = lambda: chr(random.randint(0x4E00, 0x9FFF))

        title = "".join((rchar() for _ in range(rlen)))
        desc = "".join((rchar() for _ in range(rlen2)))
        image = imageToBytes(await make_strange())
        stars = "☆"
        color = "#FF00FF"
        beforeStats = -1
    else:
        info = await get_award_info(session, uid, aid)

        if info.skinName is not None:
            title = "{0}[{1}]".format(info.awardName, info.skinName)
        else:
            title = info.awardName

        desc = info.awardDescription
        image = info.awardImg
        stars = info.levelName
        color = info.color

        beforeStats = await get_statistics(session, uid, aid)
        await add_storage(session, uid, aid, 1)

    logger.info(f"has: {beforeStats}")
    await root.emit(PlayerMergeEvent(uid, (a1, a2, a3), aid, succeed))

    name = await ctx.getSenderName()
    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderNameInGroup()

    area_title_1 = await getTextImage(
        text=f"{name} 的合成材料：",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=80,
        margin_bottom=30,
    )

    info1 = await get_award_info(session, uid, a1)
    info2 = await get_award_info(session, uid, a2)
    info3 = await get_award_info(session, uid, a3)
    box1 = await display_box(info1.color, info1.awardImg, False)
    box2 = await display_box(info2.color, info2.awardImg, False)
    box3 = await display_box(info3.color, info3.awardImg, False)
    area_material_box = await pileImages(images=[box1, box2, box3], background="#8A8580", paddingX=24, marginLeft=18, marginBottom=24)

    area_title_2 = await getTextImage(
        text=f"合成结果：{"成功" if succeed else "失败"}{"！" if succeed or aid == 89 or aid == -1 else "？"}",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=60,
        margin_bottom=18,
    )

    area_product_entry = await catch(
        title=title,
        description=desc,
        image=image,
        stars=stars,
        color=color,
        new=(beforeStats == 0),
        notation="",
    )

    area_title_3 = await getTextImage(
        text=f"本次合成花费了你 {cost} 薯片，你还有 {m - cost} 薯片。",
        color="#FFFFFF",
        font=Fonts.HARMONYOS_SANS_BLACK,
        font_size=24,
        margin_top=12,
    )

    img = await verticalPile([area_title_1, area_material_box, area_title_2, area_product_entry, area_title_3], 15, "left", "#8A8580", 60, 60, 60, 60)
    await ctx.send(UniMessage.image(raw=imageToBytes(img)))
    await session.commit()
