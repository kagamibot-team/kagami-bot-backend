from src.imports import *


@listenGroup()
@matchRegex("(zhua|抓|抓小哥)?(xb|喜报)")
async def _(ctx: GroupContext, _):
    history_list = catch_histroy_list.get_records(ctx.event.group_id)

    message: str = ""
    records: dict[str, dict[str, list[tuple[str, dict[int, PickDisplay]]]]] = {}

    for history in history_list:
        dt = timestamp_to_datetime(history.caught_time)
        dt = to_utc8(dt)

        dt_str_day = dt.strftime(r"%Y年%m月%d日")
        dt_str_time = dt.strftime(r"%H:%M:%S")

        logger.info(history.uid)

        name: str = str(history.uid)

        try:
            info = await ctx.bot.call_api(
                "get_group_member_info",
                group_id=ctx.event.group_id,
                user_id=history.qqid,
                no_cache=True,
            )
            name: str = info["nickname"]
            name = info["card"] or name
        except ActionFailed as e:
            logger.warning(e)

        if dt_str_day not in records:
            records[dt_str_day] = {}
        if name not in records[dt_str_day]:
            records[dt_str_day][name] = []
        records[dt_str_day][name].append((dt_str_time, history.displays))

    for day, datas in records.items():
        message += f"~ {day} ~\n"

        for name, get_list in datas.items():
            message += f"- 玩家 {name}\n"
            for get_info in get_list:
                message += f"在 {get_info[0]} 抓到了："
                message +=  "".join([
                                        f"{display.name} ×{display.pick.delta} ，"
                                        for _, display in get_info[1].items()
                                    ]).rstrip("，") + "；\n"
            message = message.rstrip("；\n") + "。\n\n"

    if len(message) > 0:
        await ctx.send(UniMessage().text("===== 喜报 =====\n\n" + message.rstrip("\n")))
    else:
        await ctx.send(
            UniMessage().text(
                "===== 悲报 =====\n在过去的 24 小时里，没有抓到四星或五星的记录"
            )
        )
