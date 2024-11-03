import re

from src.base.command_events import MessageContext
from src.common.command_deco import listen_message, match_regex, require_admin
from src.core.unit_of_work import get_unit_of_work


@listen_message()
@require_admin()
@match_regex(r"^:: ?给饼干 (\d+) (-?\d+)$")
async def give_cookies(ctx: MessageContext, res: re.Match[str]):
    target = int(res.group(1))
    amount = int(res.group(2))

    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(target)
        await uow.biscuit.add(uid, amount)
        now = await uow.biscuit.get(uid)

    await ctx.reply(f"给饼干成功，现在有 {now} 个饼干")


@listen_message()
@require_admin()
@match_regex(r"^:: ?查饼干 (\d+)$")
async def get_cookies(ctx: MessageContext, res: re.Match[str]):
    target = int(res.group(1))
    async with get_unit_of_work() as uow:
        uid = await uow.users.get_uid(target)
        now = await uow.biscuit.get(uid)

    await ctx.reply(f"{target} 现在有 {now} 个饼干")
