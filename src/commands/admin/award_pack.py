from typing import Any
from src.base.command_events import OnebotContext
from src.base.exceptions import ObjectNotFoundException
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
)

from arclet.alconna import Alconna, Arg, Option, Arparma

from src.core.unit_of_work import get_unit_of_work
from src.services.award_pack import get_award_pack_service


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "卡池",
        Arg("卡池名", str),
        Option("增加", Arg("增加的小哥名", str), alias=["--add", "-a", "--append"]),
        Option(
            "去除", Arg("删去的小哥名", str), alias=["--delete", "-d", "--remove", "-r"]
        ),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    pack_name = res.query[str]("卡池名")
    add_name = res.query[str]("增加的小哥名")
    sub_name = res.query[str]("删去的小哥名")

    assert pack_name is not None

    async with get_unit_of_work() as uow:
        service = get_award_pack_service()
        if not service.exist_name(pack_name):
            raise ObjectNotFoundException("卡池", pack_name)
        if add_name is not None:
            aid = await uow.awards.get_aid_strong(add_name)
            await uow.awards.add_pack(aid, pack_name)
        if sub_name is not None:
            aid = await uow.awards.get_aid_strong(sub_name)
            await uow.awards.remove_pack(aid, pack_name)

    await ctx.reply("ok.")
