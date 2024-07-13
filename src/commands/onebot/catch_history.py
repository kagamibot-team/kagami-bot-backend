from src.base.local_storage import get_localdata
from src.imports import *


@listenGroup()
@matchRegex("(zhua|抓|抓小哥)?(xb|喜报)")
async def _(ctx: GroupContext, _):
    _dates_message: dict[str, list[str]] = {}

    for qqid, xb in get_localdata().get_group_xb(ctx.event.group_id).items():
        name = await get_name(ctx.bot, qqid, ctx.event.group_id)
        _data: dict[str, list[str]] = {}

        for record in xb.records:
            key = record.time.date().strftime("%Y年%m月%d日")
            key = f"~ {key} ~"
            _data.setdefault(key, [])
            msg = record.time.strftime("%H:%M:%S")
            msg = f"在 {msg} {record.action.value}：{record.data}"
            _data[key].append(msg)
        
        for key, value in _data.items():
            _dates_message.setdefault(key, [])
            msg = f"- 玩家 {name}\n" + "；\n".join(value) + "。"
            _dates_message[key].append(msg)

    messages = [i + "\n" + "\n\n".join(v) for i, v in _dates_message.items()]

    if len(messages) > 0:
        await ctx.sendCompact(
            UniMessage().text("===== 喜报 =====\n\n" + "\n\n\n".join(messages))
        )
    else:
        await ctx.send(
            UniMessage().text(
                "===== 悲报 =====\n在过去的 24 小时里，没有抓到四星或五星的记录"
            )
        )
