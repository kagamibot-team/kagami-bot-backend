from re import Match

from loguru import logger

from src.base.command_events import MessageContext
from src.base.event.event_dispatcher import EventDispatcher
from src.base.event.event_root import root
from src.common.command_deco import kagami_exception_handler, match_regex, require_admin
from src.core.unit_of_work import get_unit_of_work
from src.services.items.base import ItemService

dispatcher = EventDispatcher()


@dispatcher.listen(MessageContext)
@kagami_exception_handler()
@require_admin()
@match_regex(r"^::给物品 (\d+) (.+?)( -?\d+)?$")
async def _(ctx: MessageContext, res: Match[str]):
    target = int(res.group(1))
    item_name: str = res.group(2)
    item_count = int(res.group(3) or 1)

    async with get_unit_of_work() as uow:
        isv = ItemService()
        _item = isv.get_item(item_name)
        if _item is not None:
            item_name = _item.name
        logger.debug(
            f"给了物品给玩家。TARGET={target}; NAME={item_name}; COUNT={item_count}"
        )
        await uow.items.give(await uow.users.get_uid(target), item_name, item_count)

    await ctx.reply("ok.")


root.link(dispatcher)
