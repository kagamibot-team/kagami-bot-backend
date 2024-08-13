from arclet.alconna import Alconna, Arg, Arparma, Option

from src.base.command_events import GroupContext
from src.base.exceptions import (
    MultipleObjectFoundException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
)
from src.common.command_decorators import (
    listen_message,
    match_alconna,
    require_admin,
)
from src.core.unit_of_work import get_unit_of_work


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(更改|设置|设定|调整|创建|添加)(别名|别名)",
        Arg("名字", str),
        Arg("别名", str),
        Option(
            "类型",
            Arg("类型名", str),
            alias=["--type", "-t"],
        ),
    )
)
async def _(ctx: GroupContext, res: Arparma):
    rname = res.query[str]("名字")
    aname = res.query[str]("别名")
    tname = res.query[str]("类型名")

    assert rname is not None and aname is not None

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid(rname)
        sid = await uow.skins.get_sid(rname)

        aidr = await uow.awards.get_aid(aname)
        sidr = await uow.skins.get_sid(aname)

        if aidr is not None or sidr is not None:
            raise ObjectAlreadyExistsException(f"{aname}")

        if aid is not None and sid is not None:
            if tname is None:
                raise MultipleObjectFoundException(rname)
            if tname == "小哥":
                await uow.awards.set_alias(aid, aname)
            elif tname == "皮肤":
                await uow.skins.set_alias(sid, aname)
        elif aid is not None:
            await uow.awards.set_alias(aid, aname)
        elif sid is not None:
            await uow.skins.set_alias(sid, aname)
        else:
            raise ObjectNotFoundException("东西", rname)

    await ctx.send("ok.")


@listen_message()
@require_admin()
@match_alconna(Alconna(["::"], "re:(删除|移除)别名", Arg("别名", str)))
async def _(ctx: GroupContext, res: Arparma):
    aname = res.query[str]("别名")
    if aname is None:
        return

    async with get_unit_of_work() as uow:
        await uow.awards.remove_alias(aname)
        await uow.skins.remove_alias(aname)

    await ctx.send("ok.")
