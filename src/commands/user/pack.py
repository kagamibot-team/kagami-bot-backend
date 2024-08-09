from typing import Any
from src.base.command_events import OnebotContext
from src.base.exceptions import ObjectNotFoundException
from src.common.decorators.command_decorators import listenOnebot, matchAlconna
from arclet.alconna import Alconna, Arg, Arparma, Option, ArgFlag

from src.core.unit_of_work import get_unit_of_work


@listenOnebot()
@matchAlconna(
    Alconna(
        "re:(小L|小l|xl)?(猎场|lc)",
        Option(
            "购买猎场",
            alias=[
                "买猎场",
                "买新猎场",
                "购置猎场",
            ],
        ),
        Option(
            "切换猎场",
            Arg("猎场序号", int, flags=[ArgFlag.OPTIONAL]),
            alias=[
                "切换",
                "前往猎场",
                "去往猎场",
                "去猎场",
                "前往",
                "去",
                "前去",
                "去往",
            ],
        ),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)
        count = await uow.user_pack.get_count(uid)
        current = await uow.user_pack.get_using(uid)
        max_count = await uow.settings.get_pack_count()

        if res.find("购买猎场"):
            if count >= max_count:
                raise ObjectNotFoundException(obj_name=f"{count + 1}号猎场")
            rest = await uow.money.use(uid, 1000)
            await uow.user_pack.set_count(uid, count + 1)
            await ctx.reply(
                (
                    f"你刚刚购买了 {count + 1} 号猎场，花费了 1000 薯片。"
                    f"\n你还剩下 {rest} 薯片。"
                    f"\n你可以输入[小L猎场 切换猎场]来切换猎场哦"
                )
            )
            return

        if res.find("切换猎场"):
            index = res.query[int]("猎场序号")
            if index is not None:
                if index <= 0 or index > count:
                    raise ObjectNotFoundException(obj_name=f"{index}号猎场")
                await uow.user_pack.set_using(uid, index)
            else:
                index = current + 1
                index -= 1
                index %= count
                index += 1
                assert 0 < index <= count
                await uow.user_pack.set_using(uid, index)
            await ctx.reply(f"已经切换到 {index} 号猎场了")
            return

    # Fallback: 没有执行任何指令时，展示默认界面
    await ctx.reply(
        f"目前总共有 {max_count} 个猎场，你已经购买了 {count} 个猎场。"
        f"现在你在 {current} 号猎场。"
    )
