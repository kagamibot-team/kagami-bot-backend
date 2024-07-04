from src.imports import *


@listenPublic()
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
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    n1 = res.query[str]("name1")
    n2 = res.query[str]("name2")
    n3 = res.query[str]("name3")

    if n1 is None or n2 is None or n3 is None:
        return

    a1 = await get_aid_by_name(session, n1)
    a2 = await get_aid_by_name(session, n2)
    a3 = await get_aid_by_name(session, n3)

    if a1 is None or a2 is None or a3 is None:
        await ctx.reply(f"Wrong {a1}, {a2}, {a3}")
        return

    aid, pos = await get_merge_result(session, a1, a2, a3)
    query = select(Award.name).filter(Award.data_id == aid)
    name = (await session.execute(query)).scalar_one()

    await ctx.reply(f"{name}, {pos}")


@listenPublic()
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
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    n1 = res.query[str]("name1")
    n2 = res.query[str]("name2")
    n3 = res.query[str]("name3")

    if n1 is None or n2 is None or n3 is None:
        return

    a1 = await get_aid_by_name(session, n1)
    a2 = await get_aid_by_name(session, n2)
    a3 = await get_aid_by_name(session, n3)

    if a1 is None or a2 is None or a3 is None:
        await ctx.reply(f"Wrong {a1}, {a2}, {a3}")
        return

    a1, a2, a3 = sorted((a1, a2, a3))

    query = select(Recipe.data_id).filter(
        Recipe.award1 == a1,
        Recipe.award2 == a2,
        Recipe.award3 == a3,
    )

    rid = (await session.execute(query)).scalar_one_or_none()
    n4 = res.query[str]("name4")
    po = res.query[float]("posi")

    if rid is None:
        if n4 is None or po is None:
            await ctx.reply(
                "这个合成配方不曾存在，合成成功率和合成出来的小哥都需要填写。"
            )
            return

        a4 = await get_aid_by_name(session, n4)

        if a4 is None:
            await ctx.reply(f"小哥 {n4} 不存在。")
            return

        await session.execute(
            insert(Recipe).values(
                award1=a1,
                award2=a2,
                award3=a3,
                result=a4,
                possibility=po,
            )
        )
        await session.commit()
        await ctx.reply("ok.")
        return

    if n4 is not None:
        a4 = await get_aid_by_name(session, n4)
        if a4 is None:
            await ctx.reply(f"小哥 {n4} 不存在。")
            return

        await session.execute(
            update(Recipe)
            .where(Recipe.data_id == rid)
            .values(
                result=a4,
            )
        )

    if po is not None:
        await session.execute(
            update(Recipe)
            .where(Recipe.data_id == rid)
            .values(
                possibility=po,
            )
        )

    await session.commit()
    await ctx.reply("ok.")
    return


@listenPublic()
@requireAdmin()
@matchAlconna(Alconna("re:(删除所有配方)", ["::"]))
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, __: Arparma):
    await session.execute(delete(Recipe))
    await ctx.send("删除成功！")