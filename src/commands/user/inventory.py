from typing import Any

from nonebot_plugin_alconna import UniMessage
from src.base.command_events import MessageContext
from src.common.command_deco import listen_message, match_alconna
from arclet.alconna import Alconna, Arg, Arparma, Option

from src.common.data.awards import get_a_list_of_award_storage
from src.common.data.user import get_user_data
from src.core.unit_of_work import get_unit_of_work
from src.ui.base.browser import get_browser_pool
from src.ui.types.common import AwardInfo
from src.ui.types.inventory import BookBoxData, DisplayBoxData, StorageData, StorageUnit
from src.ui.views.award import StorageDisplay


def build_display(
    info: list[AwardInfo],
    storage: dict[int, int] | None = None,
    stats: dict[int, int] | None = None,
) -> list[BookBoxData]:
    elements: list[BookBoxData] = []
    storage = storage or {}
    stats = stats or {}
    for d in info:
        if d.aid not in stats or stats[d.aid] <= 0:
            obj = BookBoxData(
                display_box=DisplayBoxData(
                    image="./resource/blank_placeholder.png",
                    color=d.color,
                ),
                title1=d.name,
            )
        else:
            obj = BookBoxData(
                display_box=DisplayBoxData(
                    image=d.image_url,
                    color=d.color,
                ),
                title1=d.name,
            )
            if d.level.lid >= 4:
                obj.display_box.do_glow = True
        # 如果提供了库存和统计信息，则显示之
        if d.aid in storage:
            obj.display_box.notation_down = str(storage[d.aid])
        if d.aid in stats:
            obj.display_box.notation_down = str(stats[d.aid])
        elements.append(obj)
    return elements


@listen_message()
@match_alconna(Alconna("re:(抓小?哥?|zhua)? ?(kc|库存)"))
async def _(ctx: MessageContext, res: Arparma[Any]):
    async with get_unit_of_work(ctx.sender_id) as uow:
        user = await get_user_data(ctx, uow)
        aids: dict[int, list[int]] = {}
        all_storages: list[StorageDisplay] = []
        for i in (5, 4, 3, 2, 1, 0):
            aids[i] = await uow.awards.get_aids(i)
            storages = await get_a_list_of_award_storage(uow, user.uid, aids[i])
            all_storages += [e for e in storages if e is not None]
        all_storages = sorted(
            all_storages, key=lambda s: (-s.info.level.lid, -s.storage)
        )
        _sto = {item.info.aid: item.storage for item in all_storages}
        _sta = {item.info.aid: item.stats for item in all_storages}
        infos = [item.info for item in all_storages]

        view = build_display(infos, _sto, _sta)
    img = await get_browser_pool().render(
        "storage",
        data=StorageData(
            user=user,
            boxes=[StorageUnit(elements=view)],
            title_text="库存",
        ),
    )
    await ctx.send(UniMessage.image(raw=img))
