from pathlib import Path
from typing import Any

from arclet.alconna import Alconna, Arg, Arparma, MultiVar, Option
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import MessageContext
from src.base.exceptions import SoldOutException
from src.common.command_deco import (
    limited,
    listen_message,
    match_alconna,
    require_awake,
)
from src.common.times import now_datetime
from src.core.unit_of_work import get_unit_of_work
from src.services.shop import ShopFreezed, ShopProductFreezed, build_xjshop
from src.services.stats import StatService
from src.ui.base.render import get_render_pool
from src.ui.types.common import UserData
from src.ui.types.inventory import BookBoxData, DisplayBoxData
from src.ui.types.xjshop import BuyData, Product, ProductGroup, ShopDisplay


async def shop_default_message(user: UserData, shop: ShopFreezed, money: float):
    shop_data = ShopDisplay(
        user=user,
        chips=int(money),
        products=[
            ProductGroup(
                group_name=name,
                products=[
                    BookBoxData(
                        title1=product.title,
                        title2=product.description,
                        display_box=DisplayBoxData(
                            image=product.image.url,
                            color=product.background_color,
                            notation_down=f"{int(product.price)}薯片",
                            sold_out_overlay=product.is_sold_out,
                            black_overlay=product.is_sold_out,
                        ),
                    )
                    for product in products
                ],
            )
            for name, products in shop.items()
        ],
    )

    return UniMessage().image(
        raw=await get_render_pool().render("xjshop/home", shop_data)
    )


async def shop_buy_message(
    user: UserData,
    products: list[ShopProductFreezed],
    remain: float,
):
    _date = now_datetime().strftime("%Y-%m-%d")
    _time = now_datetime().strftime("%H:%M:%S")

    data = BuyData(
        date=_date,
        time=_time,
        user=user,
        remain_chips=int(remain),
        records=[
            Product(
                title=e.title,
                price=int(e.price),
            )
            for e in products
        ],
    )

    return UniMessage.image(raw=await get_render_pool().render("xjshop/bought", data))


@listen_message()
@limited
@match_alconna(
    Alconna(
        "re:(小镜的?|xj) ?(shop|小店|商店)",
        Option(
            "买",
            alias=["购买", "购入", "buy"],
            args=Arg("商品名", MultiVar(str, flag="+")),
        ),
    )
)
@require_awake
async def _(ctx: MessageContext, res: Arparma[Any]):
    buys = res.query[list[str]]("商品名") or []

    if len(buys) == 0:
        async with get_unit_of_work(ctx.sender_id) as uow:
            uid = await uow.users.get_uid(ctx.sender_id)
            shop = await build_xjshop(uow)
            user = UserData(
                uid=uid, qqid=str(ctx.sender_id), name=await ctx.sender_name
            )
            freezed_shop = await shop.freeze(uow, uid)
            money = await uow.chips.get(uid)
            await StatService(uow).check_xjshop(uid)
        msg = await shop_default_message(user, freezed_shop, money)
        await ctx.send(msg)
    else:
        async with get_unit_of_work(ctx.sender_id) as uow:
            uid = await uow.users.get_uid(ctx.sender_id)
            shop = await build_xjshop(uow)
            user = UserData(
                uid=uid, qqid=str(ctx.sender_id), name=await ctx.sender_name
            )

            costs: float = 0
            prods: list[ShopProductFreezed] = []
            for n in buys:
                prod = shop[n]
                if await prod.is_sold_out(uow, uid):
                    raise SoldOutException(await prod.title(uow, uid))

                costs += await prod.price(uow, uid)
                prods.append(await prod.freeze(uow, uid))
                await prod.gain(uow, uid)
            remain = await uow.chips.use(uid, costs)
            await StatService(uow).xjshop_buy(uid, int(costs))
        await ctx.send(await shop_buy_message(user, prods, remain))
