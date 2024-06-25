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
    if m < 50:
        await ctx.reply(f"合成一次小哥要花 50 薯片，你的薯片不够了哟")
        return
    await set_user_money(session, uid, m - 50)

    aid = await try_merge(session, uid, a1, a2, a3)

    if aid == -1:
        rlen = random.randint(2, 4)
        rlen2 = random.randint(30, 90)
        rchar = lambda: chr(random.randint(0x4E00, 0x9FFF))

        title = "".join((rchar() for _ in range(rlen)))
        desc = "".join((rchar() for _ in range(rlen2)))
        image = imageToBytes(await make_strange())
        stars = "☆"
        color = "#FF00FF"
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

        await add_storage(session, uid, aid, 1)

    rimage = await catch(
        title=title,
        description=desc,
        image=image,
        stars=stars,
        color=color,
        new=False,
        notation="",
    )

    await ctx.reply(
        UniMessage.text(
            f"本次合成花费了你 50 薯片，你还有 {m - 50} 薯片。本次合成结果："
        ).image(raw=imageToBytes(rimage))
    )
    await session.commit()
