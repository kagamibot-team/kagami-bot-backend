import re
from typing import Any
import PIL
import PIL.Image

from arclet.alconna import Alconna, Arg, Arparma, MultiVar, Option
from nonebot_plugin_alconna import Image, UniMessage

from src.base.command_events import MessageContext
from src.base.exceptions import ObjectAlreadyExistsException, ObjectNotFoundException
from src.commands.user.inventory import build_display, calc_progress, calc_gedu
from src.common.command_deco import (
    listen_message,
    match_alconna,
    match_literal,
    match_regex,
    require_admin,
)
from src.common.data.awards import download_award_image
from src.core.unit_of_work import get_unit_of_work
from src.models.level import level_repo
from src.services.pool import PoolService
from src.ui.base.render import get_render_pool
from src.ui.types.common import UserData
from src.ui.types.inventory import BoxItemList, StorageData


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "小哥",
        ["::添加", "::创建"],
        Arg("name", str),
        Arg("level", str),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    aname = res.query[str]("name")
    lname = res.query[str]("level")
    assert aname is not None
    assert lname is not None

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid(aname)
        if aid is not None:
            raise ObjectAlreadyExistsException(aname)
        level_obj = level_repo.get_by_name(lname)
        if level_obj is None:
            raise ObjectNotFoundException("等级")
        await uow.awards.add_award(aname, level_obj.lid)
    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "小哥",
        ["::删除", "::移除"],
        Arg("name", str),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("name")
    assert name is not None

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(name)
        await uow.awards.delete_award(aid)
    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        "re:(修改|更改|调整|改变|设置|设定)小哥",
        ["::"],
        Arg("小哥原名", str),
        Option(
            "名字",
            Arg("小哥新名字", str),
            alias=["--name", "名称", "-n", "-N"],
            compact=True,
        ),
        Option(
            "等级",
            Arg("等级名字", str),
            alias=["--level", "级别", "-l", "-L"],
            compact=True,
        ),
        Option(
            "描述",
            Arg("描述", MultiVar(str, flag="+"), seps="\n"),
            alias=["--description", "-d", "-D"],
            compact=True,
        ),
        Option("图片", Arg("图片", Image), alias=["--image", "照片", "-i", "-I"]),
        Option("猎场", Arg("猎场", int), alias=["--packs", "所在猎场"]),
        Option(
            "排序优先度",
            Arg("排序优先度", int),
            alias=["--priority", "优先度", "-p", "-P"],
        ),
    )
)
async def _(ctx: MessageContext, res: Arparma):
    name = res.query[str]("小哥原名")
    newName = res.query[str]("小哥新名字")
    levelName = res.query[str]("等级名字")
    _description = res.query[tuple[str]]("描述") or ()
    image = res.query[Image]("图片")
    pack_id = res.query[int]("猎场")
    sorting = res.query[int]("排序优先度")

    assert name is not None

    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(name)
        lid = (
            uow.levels.get_by_name_strong(levelName).lid
            if levelName is not None
            else None
        )
        image = image.url if image is not None else None
        image = await download_award_image(aid, image) if image is not None else None
        await uow.awards.modify(
            aid=aid,
            name=newName,
            description="".join(_description),
            lid=lid,
            pack_id=pack_id,
            sorting=sorting,
        )

    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_literal("::抓不到的小哥")
async def _(ctx: MessageContext):
    async with get_unit_of_work() as uow:
        service = PoolService(uow)
        list = await service.get_uncatchable_aids()
    await ctx.reply(str(list))


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(所有|全部)小哥",
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
        if level_name != "":
            level = uow.levels.get_by_name_strong(level_name)
            lid = level.lid
        else:
            level = None
            lid = None

        aids = await uow.awards.get_aids(lid, pack_index)
        aids.sort()
        infos = await uow.awards.get_info_dict(aids)

        groups: list[BoxItemList] = []

        grouped_aids = await uow.awards.group_by_level(aids)
        grouped_aids_filtered = [
            (
                uow.levels.get_by_id(i),
                [v for v in vs],
            )
            for i, vs in grouped_aids.items()
        ]
        total_gedu = calc_gedu(grouped_aids_filtered)  # type: ignore

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
                _infos = sorted(_infos, key=lambda x: x.aid)
                if len(_infos) <= 0:
                    continue
                view = build_display(_infos)
                count = len(_aids[i])

                aids_level = [
                    (
                        uow.levels.get_by_id(i),
                        [v for v in _aids[i]],
                    )
                ]
                gedu = calc_gedu(aids_level)  # type: ignore
                groups.append(
                    BoxItemList(
                        title=lvl.display_name + f"：共{count}个，哥度为：{gedu}",
                        title_color=lvl.color,
                        elements=view,
                    )
                )

    pack_det = "" if pack_index is None else f"{pack_index} 猎场 "
    level_det = "" if level is None else f"{level.display_name} "
    progress_det = f" 总哥度为：{total_gedu}"

    img = await get_render_pool().render(
        "storage",
        data=StorageData(
            user=UserData(),
            boxes=groups,
            title_text=pack_det + level_det + "抓小哥进度" + progress_det,
        ),
    )
    await ctx.send_image(img)


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(test_leaderboard)",
    )
)
async def _(ctx: MessageContext, _: Arparma[Any]):
    async with get_unit_of_work(ctx.sender_id) as uow:
        pack_max = await uow.settings.get_pack_count()
        pack_progress: list[list[tuple[int, float]]] = [
            [] for _ in range(0, pack_max + 1)
        ]
        users = await uow.users.get_all_uid()
        for uid in users:
            for pid in range(0, pack_max + 1):
                lid = None
                aids = await uow.awards.get_aids(lid, pid if pid > 0 else None)
                aids2 = await uow.awards.get_aids(lid, 0)
                aids = list(set(aids) | set(aids2))
                aids.sort()

                inventory_dict = await uow.inventories.get_inventory_dict(uid, aids)
                stats_dict = {i: v[0] + v[1] for i, v in inventory_dict.items()}

                grouped_aids = await uow.awards.group_by_level(aids)
                grouped_aids_filtered = [
                    (
                        uow.levels.get_by_id(i),
                        [(v if stats_dict.get(v, 0) > 0 else None) for v in vs],
                    )
                    for i, vs in grouped_aids.items()
                ]
                if pid == 0:
                    progress = calc_gedu(grouped_aids_filtered)
                else:
                    progress = calc_progress(grouped_aids_filtered)
                pack_progress[pid].append((await uow.users.get_qqid(uid), progress))

    for pid in range(0, pack_max + 1):
        pack_progress[pid].sort(key=lambda x: x[1], reverse=True)
        progress_name = "总哥度" if pid == 0 else f"{pid}号猎场进度"
        message = f"~ {progress_name}排行榜 ~\n"
        for uid, progress in pack_progress[pid][:10]:
            if pid == 0:
                message += f"{uid}: {int(progress)}\n"
            else:
                message += f"{uid}: {progress * 100:.2f}%\n"
        await ctx.send(UniMessage.text(message))


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(test_achievement)",
        Arg("achievement", str),
    )
)
async def _(ctx: MessageContext, res: Arparma[Any]):
    achieve_dict: dict[str, list[str]] = {
        "兔子大家族": ["小沣", "小铃仙", "大学生小哥", "伪物小哥", "兔女郎小哥"],
        "小小大我": ["大我", "小我"],
        "庭师完全体": ["小妖梦", "半灵小哥"],
        "诶——这个嘛……": ["小玉手", "小哥箱"],
        "小小合成部": ["小华", "小可怜", "小水瓶子"],
    }
    achieve_name = res.query[str]("achievement")
    if achieve_name not in achieve_dict:
        return

    async with get_unit_of_work(ctx.sender_id) as uow:
        listSta: list[str] = []
        listSto: list[str] = []
        users = await uow.users.get_all_uid()
        for uid in users:
            qqid = await uow.users.get_qqid(uid)
            flagSta = True
            flagSto = True
            for award in achieve_dict[achieve_name]:
                aid = await uow.awards.get_aid(award)
                if aid is None:
                    break
                if await uow.inventories.get_stats(uid, aid) == 0:
                    flagSta = False
                if await uow.inventories.get_storage(uid, aid) == 0:
                    flagSto = False
            if flagSta:
                listSta.append(str(qqid))
            if flagSto:
                listSto.append(str(qqid))

        await ctx.send(
            UniMessage.text(
                f"成就【{achieve_name}】：\n数据库内共有{len(users)}个用户，其中{len(listSta)}个用户满足统计要求，{len(listSto)}个用户满足库存要求。"
            )
        )
        if 0 < len(listSta) < 20:
            await ctx.send(UniMessage.text("满足统计要求的：\n" + "\n".join(listSta)))
        if 0 < len(listSto) < 20:
            await ctx.send(UniMessage.text("满足库存要求的：\n" + "\n".join(listSto)))


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "re:(test_size)",
    )
)
async def _(ctx: MessageContext, res: Arparma[Any]):
    async with get_unit_of_work(ctx.sender_id) as uow:
        msg = ""
        aids = await uow.awards.get_aids()
        for aid in aids:
            award = await uow.awards.get_info(aid)
            img = PIL.Image.open(award.image_path)
            width, height = img.size
            if width != 2000:
                msg += f"{award.name}（{aid}）：{width}x{height}\n"
        await ctx.send(UniMessage.text(msg))


@listen_message()
@require_admin()
@match_regex("^:: ?全服发 ?(.+)$")
async def _(ctx: MessageContext, res: re.Match[str]):
    # 槽哥说，这个指令是万圣节活动要用的。
    # 所以我就写在这里了。
    # 你们读代码的，嗯，忽略这里吧。

    result = res.group(1)
    if result is None:
        return
    async with get_unit_of_work() as uow:
        aid = await uow.awards.get_aid_strong(result)
        uids = await uow.users.get_all_uid()
        for uid in uids:
            await uow.inventories.give(uid, aid, 1)
    await ctx.reply("给了。")
