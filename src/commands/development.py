"""
在目前的开发阶段，有很多需要用到的功能，例如同步存档之类。
如果有一些需要方便开发的指令，就写到这里吧！
"""

from pathlib import Path
from src.common.save_file_handler import pack_save
from src.imports import *


@listenGroup()
@requireAdmin()
@matchRegex(
    "^:: ?(导出|输出|保存|发送|生成|构建|建造|吐出|献出) ?(你(自己)?的)? ?(存档|文件|心脏|大脑)$"
)
@withLoading()
async def _(ctx: GroupContext, _):
    fp = await pack_save()
    await ctx.bot.call_api(
        "upload_group_file",
        group_id=ctx.event.group_id,
        file=str(fp.absolute()),
        name=fp.name,
    )


@listenPublic()
@requireAdmin()
@matchLiteral("::reload-script")
async def _(ctx: PublicContext):
    await ctx.reply("服务器即将重启")

    os.system(Path("./linux/upgrade.sh"))
