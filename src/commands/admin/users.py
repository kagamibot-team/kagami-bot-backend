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


@listen_message()
@require_admin()
@match_regex(r"^::(转移账户|账户转移|migrate-user|merge-user) (\d+) (\d+)( --merge)?$")
async def _(ctx: MessageContext, res: re.Match[str]) -> None:
    ufrom = int(res.group(2))
    uto = int(res.group(3))
    do_merge = res.group(4)

    if not do_merge:
        async with get_unit_of_work() as uow:
            uidfrom = await uow.users.get_uid(ufrom)
            uidto = await uow.users.get_uid(uto)

            await uow.users.set_qqid(uidfrom, "-1")
            await uow.users.set_qqid(uidto, str(ufrom))
            await uow.users.set_qqid(uidfrom, str(uto))

        await ctx.reply("ok")
        return

    async with get_unit_of_work() as uow:
        uidfrom = await uow.users.get_uid(ufrom)
        uidto = await uow.users.get_uid(uto)

        award_inv = await uow.inventories.get_inventory_dict(uidfrom)
        for aid, (sto, use) in award_inv.items():
            sto0, use0 = await uow.inventories.get_inventory(uidto, aid)
            await uow.inventories.set_inventory(uidfrom, aid, 0, 0)
            await uow.inventories.set_inventory(uidto, aid, sto0 + sto, use0 + use)

        chips = await uow.chips.get(uidfrom)
        chips0 = await uow.chips.get(uidto)
        await uow.chips.set(uidfrom, 0)
        await uow.chips.set(uidto, chips + chips0)

        bisc = await uow.biscuit.get(uidfrom)
        bisc0 = await uow.biscuit.get(uidto)
        await uow.biscuit.set(uidfrom, 0)
        await uow.biscuit.set(uidto, bisc + bisc0)

        flags = await uow.user_flag.get(uidfrom)
        flags0 = await uow.user_flag.get(uidto)
        await uow.user_flag.set(uidfrom, set())
        await uow.user_flag.set(uidto, flags | flags0)

        pack = await uow.user_pack.get_own(uidfrom)
        pack0 = await uow.user_pack.get_own(uidto)
        await uow.user_pack.set_own(uidfrom, {1})
        await uow.user_pack.set_own(uidto, pack | pack0)

        items = await uow.items.get_dict(uidfrom)
        for iid, (sto, use) in items.items():
            sto0, use0 = await uow.items.get(uidto, iid)
            await uow.items.set(uidfrom, iid, 0, 0)
            await uow.items.set(uidto, iid, sto + sto0, use + use0)

        skin = await uow.skin_inventory.get_list(uidfrom)
        await uow.skin_inventory.remove_all(uidfrom)
        for s in skin:
            await uow.skin_inventory.give(uidto, s)

    await ctx.reply("转移好了")
