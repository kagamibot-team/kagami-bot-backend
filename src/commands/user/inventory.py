from typing import Any
from src.base.command_events import MessageContext
from src.common.command_deco import listen_message, match_alconna
from arclet.alconna import Alconna, Arg, Arparma, Option

from src.ui.types.common import AwardInfo
from src.ui.types.inventory import BookBoxData


def build_display(info: list[AwardInfo]) -> list[BookBoxData]: ...


@listen_message()
@match_alconna(Alconna("re:(抓小?哥?|zhua) ?(kc|库存)"))
async def _(ctx: MessageContext, res: Arparma[Any]): ...
