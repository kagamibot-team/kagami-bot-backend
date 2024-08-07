from src.base.command_events import OnebotContext
from src.common.decorators.command_decorators import listenOnebot, matchLiteral
from src.core.unit_of_work import get_unit_of_work


@listenOnebot()
@matchLiteral("切换猎场")
async def _(ctx: OnebotContext):
    async with get_unit_of_work(ctx.sender_id) as uow:
        uid = await uow.users.get_uid(ctx.sender_id)

        pools = list(await uow.users.get_own_packs(uid))
        current = await uow.users.hanging_pack(uid)

        result: None | str = None
        if current is None:
            if len(pools) > 0:
                result = pools[0]
        elif current in pools:
            if current != pools[-1]:
                result = pools[pools.index(current) + 1]

        await uow.users.hang_pack(uid, result)

    result = result or "默认猎场"

    await ctx.reply(f"已经切换到 {result} 了")
