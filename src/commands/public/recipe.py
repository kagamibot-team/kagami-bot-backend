from src.imports import *


@listenPublic()
@requireAdmin()
@matchAlconna(
    Alconna(
        "re:(查配方|cpf|pf)",
        ["::"],
        Arg("name1", str),
        Arg("name2", str),
        Arg("name3", str),
    )
)
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    await clear_all_recipe(session)

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
