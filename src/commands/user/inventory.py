from typing import Any, Iterable

from loguru import logger
from nonebot_plugin_alconna import UniMessage
from src.base.command_events import MessageContext
from src.base.exceptions import KagamiRangeError
from src.common.command_deco import listen_message, match_alconna
from arclet.alconna import Alconna, Arg, Arparma, Option

from src.common.data.user import get_user_data
from src.core.unit_of_work import get_unit_of_work
from src.models.level import Level
from src.ui.base.browser import get_browser_pool
from src.ui.types.common import AwardInfo, UserData
from src.ui.types.inventory import BookBoxData, DisplayBoxData, StorageData, BoxItemList


def build_display(
    info: list[AwardInfo],
    storage: dict[int, int] | None = None,
    stats: dict[int, int] | None = None,
) -> list[BookBoxData]:
    elements: list[BookBoxData] = []

    for d in info:
        if stats is not None and (d.aid not in stats or stats[d.aid] <= 0):
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
        if storage is not None and d.aid in storage:
            obj.display_box.notation_down = str(storage[d.aid])
        if stats is not None and d.aid in stats:
            obj.display_box.notation_down = str(stats[d.aid])
        elements.append(obj)
    return elements


def calc_progress(grouped_awards: Iterable[tuple[Level, list[int | None]]]) -> float:
    "进度"
    param: int = 10  # 榆木华定义的常数
    denominator: float = 0
    progress: float = 0

    for level, awards in grouped_awards:
        if level.weight == 0:
            continue
        numerator: float = 1 / (level.weight ** (1 / param))
        logger.info(
            f"{level.display_name}: {level.weight} ^ {1 / param} = " f"{numerator}"
        )
        denominator += numerator
        if len(awards) != 0:
            progress += numerator * (
                len([a for a in awards if a is not None]) / len(awards)
            )
        else:
            progress += 1 * numerator

    return progress / denominator if denominator != 0 else 0


@listen_message()
@match_alconna(Alconna("re:(抓小?哥?|zhua)? ?(kc|库存)"))
async def _(ctx: MessageContext, res: Arparma[Any]):
    async with get_unit_of_work(ctx.sender_id) as uow:
        user = await get_user_data(ctx, uow)
        aids = await uow.awards.get_aids()
        infos = list((await uow.awards.get_info_dict(aids)).values())
        inventory_dict = await uow.inventories.get_inventory_dict(user.uid, aids)

    storage_dict = {i: v[0] for i, v in inventory_dict.items()}
    stats_dict = {i: v[0] + v[1] for i, v in inventory_dict.items()}
    infos = [i for i in infos if stats_dict.get(i.aid, 0) > 0]
    infos = sorted(
        infos,
        key=lambda i: (-i.level.lid, -storage_dict.get(i.aid, 0), i.sorting, i.aid),
    )
    view = build_display(infos, storage_dict, stats_dict)
    img = await get_browser_pool().render(
        "storage",
        data=StorageData(
            user=user,
            boxes=[BoxItemList(elements=view)],
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
            level = uow.levels.get_by_name_strong(level_name)
            lid = level.lid
        else:
            level = None
            lid = None
        pack_max = await uow.settings.get_pack_count()
        if pack_index is not None and (pack_index <= 0 or pack_index > pack_max):
            raise KagamiRangeError(
                "猎场序号", f"大于 0 且不超过 {pack_max} 的值", pack_index
            )

        aids = await uow.awards.get_aids(lid, pack_index)
        infos = await uow.awards.get_info_dict(aids)

        inventory_dict = await uow.inventories.get_inventory_dict(user.uid, aids)

        storage_dict = {i: v[0] for i, v in inventory_dict.items()}
        stats_dict = {i: v[0] + v[1] for i, v in inventory_dict.items()}

        groups: list[BoxItemList] = []

        if lid is not None:
            infos = [infos[aid] for aid in aids]
            view = build_display(infos, storage_dict, stats_dict)
            groups.append(BoxItemList(elements=view))
            progress = 0
        else:
            grouped_aids = await uow.awards.group_by_level(aids)
            grouped_aids_filtered = [
                (
                    uow.levels.get_by_id(i),
                    [(v if stats_dict.get(v, 0) > 0 else None) for v in vs],
                )
                for i, vs in grouped_aids.items()
            ]
            progress = calc_progress(grouped_aids_filtered)

            for i in (5, 4, 3, 2, 1, 0):
                if i not in grouped_aids:
                    continue

                lvl = uow.levels.get_by_id(i)
                _infos = [infos[aid] for aid in grouped_aids[i]]
                if i == 0:
                    # 零星小哥的特殊处理
                    _infos = [i for i in _infos if stats_dict.get(i.aid, 0) > 0]
                if len(_infos) <= 0:
                    continue
                view = build_display(_infos, storage_dict, stats_dict)
                current = len([i for i in grouped_aids[i] if stats_dict.get(i, 0) > 0])
                progress_follow = f"：{current}/{len(grouped_aids[i])}" if i > 0 else ""
                groups.append(
                    BoxItemList(
                        title=lvl.display_name + progress_follow,
                        title_color=lvl.color,
                        elements=view,
                    )
                )

    pack_det = "" if pack_index is None else f"{pack_index} 猎场 "
    level_det = "" if level is None else f"{level.display_name} "
    progress_det = "" if level is not None else f" {progress * 100:.2f}%"

    img = await get_browser_pool().render(
        "storage",
        data=StorageData(
            user=user,
            boxes=groups,
            title_text=pack_det + level_det + "抓小哥进度" + progress_det,
        ),
    )
    await ctx.send(UniMessage.image(raw=img))


@listen_message()
@match_alconna(
    Alconna(
        ["::"],
        "re:(所有|全部)小哥",
        Option(
            "等级",
            Arg("等级名字", str),
            alias=["--level", "级别", "-l", "-L"],
            compact=True,
        ),
        Option(
            "猎场",
            Arg("猎场序号", int),
            alias=["--pack", "小鹅猎场", "-p", "-P"],
            compact=True,
        ),
    )
)
async def _(ctx: MessageContext, res: Arparma[Any]):
    level_name = res.query[str]("等级名字") or ""
    pack_index = res.query[int]("猎场序号")

    async with get_unit_of_work(ctx.sender_id) as uow:
        if level_name != "":
            level = uow.levels.get_by_name_strong(level_name)
            lid = level.lid
        else:
            level = None
            lid = None
        pack_max = await uow.settings.get_pack_count()
        if pack_index is not None and (pack_index <= 0 or pack_index > pack_max):
            raise KagamiRangeError(
                "猎场序号", f"大于 0 且不超过 {pack_max} 的值", pack_index
            )

        aids = await uow.awards.get_aids(lid, pack_index)
        infos = await uow.awards.get_info_dict(aids)

        groups: list[BoxItemList] = []

        if lid is not None:
            infos = [infos[aid] for aid in aids]
            view = build_display(infos)
            groups.append(BoxItemList(elements=view))
        else:
            _aids = await uow.awards.group_by_level(aids)

            for i in (5, 4, 3, 2, 1, 0):
                if i not in _aids:
                    continue

                lvl = uow.levels.get_by_id(i)
                _infos = [infos[aid] for aid in _aids[i]]
                if len(_infos) <= 0:
                    continue
                view = build_display(_infos)
                groups.append(
                    BoxItemList(
                        title=lvl.display_name,
                        title_color=lvl.color,
                        elements=view,
                    )
                )

    pack_det = "" if pack_index is None else f"{pack_index} 猎场 "
    level_det = "" if level is None else f"{level.display_name} "

    img = await get_browser_pool().render(
        "storage",
        data=StorageData(
            user=UserData(),
            boxes=groups,
            title_text=pack_det + level_det + "抓小哥进度",
        ),
    )
    await ctx.send(UniMessage.image(raw=img))
