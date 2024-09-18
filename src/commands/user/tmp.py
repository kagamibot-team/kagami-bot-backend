from typing import Any, Iterable

from loguru import logger
from nonebot_plugin_alconna import UniMessage
from src.base.command_events import MessageContext
from src.common.command_deco import listen_message, match_alconna, require_admin
from arclet.alconna import Alconna, Arg, Arparma, Option

from src.core.unit_of_work import get_unit_of_work

@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(test_checkrecipe)",
    )
)
async def _(ctx: MessageContext, _: Arparma[Any]):
    res: str = ""
    async with get_unit_of_work(ctx.sender_id) as uow:
        for rid in range(1, 16881):
            logger.info(rid)
            info = await uow.recipes.get_recipe_info(rid)
            if info is None:
                continue
            pid1 = await uow.pack.get_main_pack(info.aid1)
            n1 = (await uow.awards.get_info(info.aid1)).name
            pid2 = await uow.pack.get_main_pack(info.aid2)
            n2 = (await uow.awards.get_info(info.aid2)).name
            pid3 = await uow.pack.get_main_pack(info.aid3)
            n3 = (await uow.awards.get_info(info.aid3)).name
            pidr = await uow.pack.get_main_pack(info.result)
            nr = (await uow.awards.get_info(info.result)).name
            if pidr > 0 and pid1 != pidr and pid2 != pidr and pid3 != pidr:
                await uow.recipes.reset_recipe(info.aid1, info.aid2, info.aid3)
                res+=f"{rid}: {n1} + {n2} + {n3} -> {nr}\n"
    await ctx.send(f"res: {res}")