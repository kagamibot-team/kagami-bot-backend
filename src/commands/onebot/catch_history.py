from src.imports import *


@listenGroup()
@matchRegex("(zhua|抓|抓小哥)?(xb|喜报)")
async def _(ctx: GroupContext, _):
    history_list = catch_histroy_list.get_records(ctx.event.group_id)

    messages: list[str] = []

    for history in history_list:
        dt = timestamp_to_datetime(history.caught_time)
        dt = to_utc8(dt)

        dt_str = dt.strftime(r"%Y年%m月%d日 %H:%M:%S")

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

        messages.append(
            f"{name} 在 {dt_str} 抓到了："
            + "".join(
                [
                    f"\n- {display.name} × {display.pick.delta}"
                    for _, display in history.displays.items()
                ]
            )
        )

    if len(messages) > 0:
        await ctx.send(UniMessage().text("===== 喜报 =====\n" + "\n\n".join(messages)))
    else:
        await ctx.send(
            UniMessage().text(
                "===== 悲报 =====\n在过去的 24 小时里，没有抓到四星或五星的记录"
            )
        )
