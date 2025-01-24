"""
在目前的开发阶段，有很多需要用到的功能，例如同步存档之类。
如果有一些需要方便开发的指令，就写到这里吧！
"""

import json
from pathlib import Path
from re import Match
import re
import time
from typing import Any

from arclet.alconna import Alconna, Arg, Arparma, Option
from nonebot_plugin_alconna import UniMessage

from src.apis.render_ui import manager as backend_data_manager
from src.base.command_events import GroupContext, MessageContext, OnebotContext
from src.base.db import DatabaseManager
from src.base.onebot.onebot_api import get_group_list
from src.base.onebot.onebot_tools import update_cached_name
from src.base.res import KagamiResourceManagers
from src.base.res.strategy import FileStorageStrategy
from src.common import config
from src.common.command_deco import (
    listen_message,
    match_alconna,
    match_literal,
    match_regex,
    require_admin,
)
from src.common.save_file_handler import pack_save
from src.core.unit_of_work import get_unit_of_work
from src.ui.base.rabbitmq_worker import RabbitMQWorker
from src.ui.base.render import (
    ChromeBrowserWorker,
    FirefoxBrowserWorker,
    get_render_pool,
)


@listen_message()
@require_admin()
@match_literal("::manual-save")
async def _(ctx: MessageContext):
    await DatabaseManager.get_single().manual_checkpoint()
    await ctx.reply("ok")


@listen_message()
@require_admin()
@match_regex(
    "^:: ?(导出|输出|保存|发送|生成|构建|建造|吐出|献出) ?(你(自己)?的)? ?(存档|文件|心脏|大脑)$"
)
async def _(ctx: GroupContext, _):
    await DatabaseManager.get_single().manual_checkpoint()
    fp = await pack_save()
    await ctx.bot.call_api(
        "upload_group_file",
        group_id=ctx.event.group_id,
        file=str(fp.absolute()),
        name=fp.name,
    )


@listen_message()
@require_admin()
@match_regex("^::导出日志$")
async def _(ctx: GroupContext, _):
    await DatabaseManager.get_single().manual_checkpoint()
    fp = Path("./data/log.log")
    await ctx.bot.call_api(
        "upload_group_file",
        group_id=ctx.event.group_id,
        file=str(fp.absolute()),
        name=fp.name,
    )


@listen_message()
@require_admin()
@match_regex("^::导出报错$")
async def _(ctx: GroupContext, _):
    await DatabaseManager.get_single().manual_checkpoint()
    fp = Path("./data/error.log")
    await ctx.bot.call_api(
        "upload_group_file",
        group_id=ctx.event.group_id,
        file=str(fp.absolute()),
        name=fp.name,
    )


@listen_message()
@require_admin()
@match_regex("^::dump-data ([0-9a-fA-F]+)$")
async def _(ctx: MessageContext, res: Match[str]):
    data = backend_data_manager.get(res.group(1))
    if data is not None:
        if isinstance(data, dict):
            await ctx.reply(UniMessage(json.dumps(data)))
        else:
            await ctx.reply(UniMessage(str(data.model_dump_json(indent=4))))
    else:
        await ctx.reply("None.")


@listen_message()
@require_admin()
@match_literal("::refresh-card")
async def _(ctx: OnebotContext):
    groups = await get_group_list(ctx.bot)
    for info in groups:
        await update_cached_name(ctx.bot, info.group_id)
    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_alconna(
    Alconna(
        ["::"],
        "browser-pool",
        Option("--list", alias=["-l"]),
        Option("--reload", Arg("browser_work_id", str), alias=["-r"]),
        Option("--clean", alias=["-c"]),
        Option("--reload-all", alias=["-a"]),
        Option("--push", Arg("browser_type", str), alias="-p"),
        Option("--kill", Arg("browser_work_id", str), alias=["-k"]),
    )
)
async def _(ctx: GroupContext, res: Arparma[Any]):
    pool = get_render_pool()

    if res.exist("list"):
        ls = "当前闲置的渲染器："
        idle, working, starting = await pool.get_worker_list()
        for worker in idle:
            ls += "\n- " + str(worker)
        ls += "\n\n当前正在工作的渲染器："
        for worker in working:
            ls += (
                "\n- "
                + str(worker)
                + f" 已经工作 {time.time() - worker.last_render_begin:.2f} 秒了"
            )
        ls += "\n\n当前正在启动的渲染器："
        for worker in starting:
            ls += "\n- " + str(worker)
        await ctx.reply(ls)
        return

    if res.exist("reload"):
        work_id = res.query[str]("browser_work_id")
        assert work_id is not None
        await pool.reload(work_id)
        await ctx.reply("ok.")
        return

    if res.exist("clean"):
        await pool.clean()
        await ctx.reply("ok.")
        return

    if res.exist("reload-all"):
        await pool.reload()
        await ctx.reply("ok.")
        return

    if res.exist("push"):
        br_type = res.query[str]("browser_type") or ""
        if br_type.upper() == "CHROME":
            await pool.put(ChromeBrowserWorker)
            await ctx.reply("ok.")
        elif br_type.upper() == "FIREFOX":
            await pool.put(FirefoxBrowserWorker)
            await ctx.reply("ok.")
        elif br_type.upper() == "RABBITMQ":
            await pool.put(
                lambda: RabbitMQWorker(
                    config.get_config().rabbitmq_host,
                    config.get_config().rabbitmq_port,
                    config.get_config().rabbitmq_virtual_host,
                    config.get_config().rabbitmq_account,
                    config.get_config().rabbitmq_password,
                )
            )
            await ctx.reply("ok.")
        else:
            await ctx.reply(f"未知的渲染器类型：{br_type}")
        return

    if res.exist("kill"):
        work_id = res.query[str]("browser_work_id")
        assert work_id is not None
        await pool.kill(work_id)
        await ctx.reply("ok.")
        return

    await ctx.reply(
        "Usage:\n"
        "::browser-pool --list # 列出当前正在工作的渲染器\n"
        "::browser-pool --reload <browser_work_id>  # 重载指定渲染器\n"
        "::browser-pool --clean  # 清理不可用的渲染器\n"
        "::browser-pool --reload-all  # 重载所有渲染器"
    )


@listen_message()
@require_admin()
@match_literal("::clear-shadow-cache")
async def _(ctx: MessageContext):
    shadow = KagamiResourceManagers.xiaoge_low.shadow
    assert isinstance(shadow, FileStorageStrategy)
    files = [f for f in shadow.root.iterdir()]
    for file in files:
        file.unlink(True)
    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_literal("::migrate-skin-level")
async def _(ctx: MessageContext):
    async with get_unit_of_work() as uow:
        level1 = "半条拖，走路炸弹兵，戴帽海盗，禁言，地鼠，神鹰，黑暗骑士，篮球，卡卡，大猫耳，无语企鹅，双子向日葵，暹罗，萌死哥Ⅱ，全模仿，匿奇，歼世，新月，🗿，曾哥，硬汉，小林，猫猫凉，大脸妹，中二病，哥别林"
        level2 = "鬼子兵，最强，豌豆喷子，我的战争，快乐小登，透明人间，异端，凹小华，海森哥，杰拉鲁星哥，捣蛋猪，黑猴子，强尼银手，花心超人，拔叔，玩游戏机，生气太阳，冰糖葫芦，断罪，五星上将，犬作，1437小帝，超级塞亚哥，欢喜哥"
        level3 = "骚灵三皮奶，顽皮偶像，JOKER，最终鬼畜妹，戴帽反色觉，女仆装，蜂巢，iMasuo，薯片霓虹，百变小哥系列，孜然赠予你，人类之心，小魅影，赤蛮奇wum，忍杀"
        level4 = "我喜欢你，终极小望，债台高筑，很开心哦，骗吃骗喝，水塔将倾，文学少女，完美冻结，卒业式后，尼禄，千小本樱，极地小冲击，嘿嘿嗤笑，漫天花雨，填满灵魂，圆环之理，恶魔银庭"
        n_cd = "谎言舞者，超预告篇，小兔子洞，小小的我，三要素，小泡壳，研究员华，紫杀幽灵，卷毛鱼小哥"

        for sid in await uow.skins.all_sid():
            info = await uow.skins.get_info_v2(sid)
            if info.name in level1:
                info.level = 1
            elif info.name in level2:
                info.level = 2
            elif info.name in level3:
                info.level = 3
            elif info.name in level4:
                info.level = 4
            else:
                info.level = 0

            if info.name in n_cd:
                info.can_draw = False
            else:
                info.can_draw = True
            await uow.skins.set_info_v2(sid, info)
    await ctx.reply("ok.")


@listen_message()
@require_admin()
@match_regex(r"^::render (\S+) ([0-9a-fA-F]+)$")
async def _(ctx: MessageContext, res: re.Match[str]):
    page_name = res.group(1)
    data_hex = res.group(2)

    assert page_name is not None
    assert data_hex is not None
    
    img = await get_render_pool().render(page_name, data=data_hex)
    await ctx.send_image(img)
