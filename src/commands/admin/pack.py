from typing import Any

from arclet.alconna import Alconna, Arg, ArgFlag, Arparma, Option

from src.base.command_events import OnebotContext
from src.base.exceptions import KagamiRangeError, ObjectAlreadyExistsException
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    requireAdmin,
)
from src.core.unit_of_work import get_unit_of_work
from src.repositories.up_pool_repository import UpPoolInfo
from src.services.pool import PoolService


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "猎场设置",
        Option("开放猎场数", Arg("猎场数", int), alias=["猎场数", "-n"]),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    pack_count: int | None = res.query[int]("猎场数")

    async with get_unit_of_work() as uow:
        if pack_count is not None:
            await uow.settings.set_pack_count(pack_count)

    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "re:(创建|添加|新增|增加)猎场up",
        Arg("名称", str),
        Arg("所属猎场", int),
        Arg("价格", int, flags=[ArgFlag.OPTIONAL]),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    name = res.query[str]("名称") or ""
    pack = res.query[int]("所属猎场") or 0
    cost = res.query[int]("价格") or -1
    async with get_unit_of_work() as uow:
        if pack <= 0:
            raise KagamiRangeError("猎场 ID", "大于 0 的值", pack)
        upid = await uow.up_pool.get_upid(name)
        if upid is not None:
            raise ObjectAlreadyExistsException(name)
        await uow.up_pool.create_pool(pack, name, cost)
    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "删除猎场up",
        Arg("名字", str),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    name = res.query[str]("名字") or ""
    async with get_unit_of_work() as uow:
        upid = await uow.up_pool.get_upid_strong(name)
        await uow.up_pool.remove_pool(upid)
    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "更改猎场up",
        Arg("原名", str),
        Option("名字", Arg("新名字", str), alias=("新名字", "--name", "-n")),
        Option("所属猎场", Arg("猎场 ID", int), alias=("猎场", "--pack", "-p")),
        Option(
            "价格",
            Arg("价格数", int),
            alias=["价钱", "金钱", "薯片", "消耗", "--cost", "-c"],
        ),
        Option("添加小哥", Arg("添加小哥名", str), alias=["增加小哥", "--add", "-a"]),
        Option(
            "去除小哥",
            Arg("去除小哥名", str),
            alias=["移除小哥", "删除小哥", "删去小哥", "--remove", "-r"],
        ),
    )
)
async def _(ctx: OnebotContext, res: Arparma[Any]):
    rname = res.query[str]("原名") or ""
    nname = res.query[str]("新名字")
    pack = res.query[int]("猎场 ID")
    cost = res.query[int]("价格数")

    add = res.query[str]("添加小哥名")
    sub = res.query[str]("去除小哥名")

    async with get_unit_of_work() as uow:
        upid = await uow.up_pool.get_upid_strong(rname)
        if nname is not None:
            upid2 = await uow.up_pool.get_upid(nname)
            if upid2 is not None:
                raise ObjectAlreadyExistsException(nname)
        await uow.up_pool.modify(
            upid=upid,
            belong_pack=pack,
            name=nname,
            cost=cost,
        )

        if add is not None:
            await uow.up_pool.add_aid(upid, await uow.awards.get_aid_strong(add))
        if sub is not None:
            await uow.up_pool.remove_aid(upid, await uow.awards.get_aid_strong(sub))

    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna(["::"], "展示猎场up", Arg("名字", str)))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    name = res.query[str]("名字") or ""

    async with get_unit_of_work() as uow:
        upid = await uow.up_pool.get_upid_strong(name)
        info = await uow.up_pool.get_pool_info(upid)

        anames = await uow.up_pool.get_award_names(upid)

    await ctx.reply(str((info, anames)))


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna(["::"], "re:上架猎场[uU][pP]", Arg("名字", str)))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    name = res.query[str]("名字") or ""

    async with get_unit_of_work() as uow:
        service = PoolService(uow)
        rs = await service.hang_up_pool(name)

    await ctx.reply(f"已经将 {name} 的上架设置为 {rs} 状态了，同一猎场其他的已经下架")


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna(["::"], "添加关联猎场", Arg("小哥名", str), Arg("猎场ID", int)))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    name = res.query[str]("小哥名") or ""
    pack = res.query[int]("猎场ID") or -1
    async with get_unit_of_work() as uow:
        service = PoolService(uow)
        await service.add_award_linked_pack(name, pack)
    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna(["::"], "删除关联猎场", Arg("小哥名", str), Arg("猎场ID", int)))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    name = res.query[str]("小哥名") or ""
    pack = res.query[int]("猎场ID") or -1
    async with get_unit_of_work() as uow:
        service = PoolService(uow)
        await service.remove_award_linked_pack(name, pack)
    await ctx.reply("ok.")


@listenOnebot()
@requireAdmin()
@matchAlconna(Alconna(["::"], "展示猎场", Arg("序号", int)))
async def _(ctx: OnebotContext, res: Arparma[Any]):
    pack = res.query[int]("序号")
    assert pack is not None

    async with get_unit_of_work() as uow:
        main_aids = await uow.pack.get_main_aids_of_pack(pack)
        linked_aids = await uow.pack.get_linked_aids_of_pack(pack)

        main_names = set((await uow.awards.get_names(main_aids)).values())
        linked_names = set((await uow.awards.get_names(linked_aids)).values())

        pool_ids = await uow.up_pool.get_pools_of_pack(pack)
        pools: list[UpPoolInfo] = []
        for pool in pool_ids:
            pools.append(await uow.up_pool.get_pool_info(pool))

    await ctx.send(
        f"=== {pack} 号猎场 ===\nMAIN={main_names}\nLINKED={linked_names}\nCONTAIN_POOLS={pools}"
    )
