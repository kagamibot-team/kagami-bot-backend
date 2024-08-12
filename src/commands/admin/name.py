from typing import Any
from src.base.command_events import GroupContext
from src.common.decorators.command_decorators import (
    listen_message,
    match_alconna,
    require_admin,
)
from arclet.alconna import Alconna, Arg, ArgFlag, Arparma

from src.core.unit_of_work import get_unit_of_work


@listen_message()
@require_admin()
@match_alconna(
    Alconna(["::"], "叫", Arg("QQ号", int), Arg("名字", str, flags=[ArgFlag.OPTIONAL]))
)
async def _(ctx: GroupContext, res: Arparma[Any]):
    qqid = res.query[int]("QQ号", -1)
    name = res.query[str]("名字")

    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(qqid)
        await uow.users.set_name(uid, name)

    await ctx.reply("ok")
