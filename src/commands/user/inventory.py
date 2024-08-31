from typing import Any

from nonebot_plugin_alconna import UniMessage
from src.base.command_events import MessageContext
from src.base.exceptions import KagamiRangeError
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
                    color="#696361",
                ),
                title1="？？？",
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


@listen_message()
@match_alconna(
    Alconna(
        "re:(zhuajd|抓进度|抓小哥进度)",
        Option(
            "等级",
            Arg("等级名字", str),
            alias=["--level", "级别", "-l", "-L", "lv"],
            compact=True,
        ),
        Option(
            "猎场",
            Arg("猎场序号", int),
            alias=["--pack", "小鹅猎场", "-p", "-P", "lc"],
            compact=True,
        ),
    )
)
async def _(ctx: MessageContext, res: Arparma[Any]):
    level_name = res.query[str]("等级名字") or ""
    pack_index = res.query[int]("猎场序号")

    async with get_unit_of_work(ctx.sender_id) as uow:
        user = await get_user_data(ctx, uow)
        if level_name != "":
            lid = uow.levels.get_by_name_strong(level_name).lid
        else:
            lid = None
        pack_max = await uow.settings.get_pack_count()
        if pack_index is not None and (pack_index <= 0 or pack_index > pack_max):
            raise KagamiRangeError(
                "猎场序号", f"大于 0 且不超过 {pack_max} 的值", pack_index
            )

        aids = await uow.awards.get_aids(lid, pack_index)
        inventory_dict = await uow.inventories.get_inventory_dict(user.uid, aids)
        storage_dict = {i: v[0] for i, v in inventory_dict.items()}
        stats_dict = {i: v[0] + v[1] for i, v in inventory_dict.items()}
        infos = await uow.awards.get_info_dict(aids)

        groups: list[StorageUnit] = []

        if lid is not None:
            infos = [infos[aid] for aid in aids]
            view = build_display(infos, storage_dict, stats_dict)
            groups.append(StorageUnit(elements=view))
        else:
            _aids = await uow.awards.group_by_level(aids)

            for i in (5, 4, 3, 2, 1, 0):
                if i not in _aids:
                    continue

                lvl = uow.levels.get_by_id(i)
                _infos = [infos[aid] for aid in _aids[i]]
                if i == 0:
                    # 零星小哥的特殊处理
                    _infos = [i for i in _infos if stats_dict.get(i.aid, 0) > 0]
                if len(_infos) <= 0:
                    continue
                view = build_display(_infos, storage_dict, stats_dict)
                current = len([i for i in _aids[i] if stats_dict.get(i, 0) > 0])
                progress_follow = f"：{current}/{len(_aids[i])}" if i > 0 else ""
                groups.append(
                    StorageUnit(
                        title=lvl.display_name + progress_follow,
                        title_color=lvl.color,
                        elements=view,
                    )
                )

    img = await get_browser_pool().render(
        "storage",
        data=StorageData(
            user=user,
            boxes=groups,
            title_text="抓小哥进度",
        ),
    )
    await ctx.send(UniMessage.image(raw=img))

