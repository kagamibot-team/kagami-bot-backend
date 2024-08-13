from typing import Any

import PIL.Image
import qrcode
import qrcode.constants
import qrcode.main
from arclet.alconna import Alconna, Arg, Arparma, MultiVar, Option
from nonebot_plugin_alconna import UniMessage

from src.base.command_events import MessageContext
from src.base.exceptions import SoldOutException
from src.common.command_decorators import (
    listen_message,
    match_alconna,
)
from src.common.times import now_datetime
from src.core.unit_of_work import get_unit_of_work
from src.services.shop import ShopFreezed, ShopProductFreezed, build_xjshop
from src.ui.base.basics import Fonts, paste_image, pile, render_text, vertical_pile
from src.ui.base.tools import image_to_bytes
from src.ui.components.awards import ref_book_box_raw
from src.ui.views.user import UserData


async def product_box(product: ShopProductFreezed):
    return ref_book_box_raw(
        color=product.background_color,
        image=product.image,
        new=False,
        notation_bottom=str(product.price) + "薯片",
        notation_top="",
        name=product.title,
        name_bottom=product.description,
        sold_out=product.is_sold_out,
        smaller_size=True,
    )


async def shop_default_message(user: UserData, shop: ShopFreezed, money: float):
    titles: list[PIL.Image.Image] = []
    boxes: list[PIL.Image.Image] = []

    titles.append(
        render_text(
            text=(
                f"欢迎来到小镜商店，{user.name}！您拥有{int(money)}薯片。\n"
                "输入“小镜商店 购买 {商品名}”就可以购买了。\n"
            ),
            width=808 - 80 * 2,
            color="#FFFFFF",
            font=Fonts.HARMONYOS_SANS_BLACK,
            font_size=32,
        )
    )

    for group, products in shop.items():
        boxes.append(
            render_text(
                text=group,
                color="#FFFFFF",
                font=Fonts.HARMONYOS_SANS_BLACK,
                font_size=60,
            )
        )

        subs: list[PIL.Image.Image] = []
        for product in products:
            subs.append(await product_box(product))
        boxes.append(
            pile(
                images=subs,
                columns=3,
                background="#9B9690",
                horizontalAlign="center",
                marginBottom=30,
            )
        )

    area_title = vertical_pile(titles, 0, "left", "#9B9690", 0, 0, 0, 0)
    area_box = vertical_pile(boxes, 0, "left", "#9B9690", 0, 0, 0, 0)
    image = vertical_pile(
        [area_title, area_box], 40, "left", "#9B9690", 464, 80, 80, 60
    )
    image.paste(PIL.Image.open("./res/kagami_shop.png"), (0, 0))

    return UniMessage().image(raw=image_to_bytes(image))


async def shop_buy_message(
    user: UserData,
    products: list[ShopProductFreezed],
    cost: float,
    remain: float,
):
    buy_result = "小镜的 Shop 销售小票\n"
    buy_result += "--------------------\n"
    buy_result += f"日期：{now_datetime().strftime('%Y-%m-%d')}\n"
    buy_result += f"时间：{now_datetime().strftime('%H:%M:%S')}\n"
    buy_result += f"客户：{user.name}\n"
    buy_result += f"编号：{user.qqid}\n"
    buy_result += "--------------------\n\n"

    for product in products:
        buy_result += f"- {product.title}  {product.price} 薯片\n"

    buy_result += "\n"
    buy_result += f"总计：{cost}薯片\n"
    buy_result += f"实付：{cost}薯片\n"
    buy_result += f"余额：{remain}薯片\n"
    buy_result += "--------------------\n"
    buy_result += "  本次消费已结帐\n"
    buy_result += "  欢迎下次光临\n"
    buy_result += "--------------------\n"

    image = render_text(
        text=buy_result,
        width=336,
        color="#000000",
        font=Fonts.VONWAON_BITMAP_12,
        font_size=24,
        margin_top=60,
        margin_bottom=248,
        margin_left=20,
        margin_right=20,
        draw_emoji=False,
    )

    base = PIL.Image.new("RGBA", image.size, "#FFFFFF")
    paste_image(base, image, 0, 0)

    qrc = qrcode.main.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qrc.add_data(buy_result)
    qrc.make(fit=True)
    qimg = qrc.make_image(fill_color="black", back_color="white")

    qr = qimg.resize((180, 180), PIL.Image.LANCZOS)

    base.paste(qr, (98, base.height - 240))
    return UniMessage.image(raw=image_to_bytes(base))


@listen_message()
@match_alconna(
    Alconna(
        "re:(小镜的?|xj) ?(shop|小店|商店)",
        Option(
            "买",
            alias=["购买", "购入", "buy"],
            args=Arg("商品名列表", MultiVar(str, flag="+")),
        ),
    )
)
async def _(ctx: MessageContext, res: Arparma[Any]):
    buys = res.query[list[str]]("商品名列表") or []

    if len(buys) == 0:
        async with get_unit_of_work(ctx.sender_id) as uow:
            uid = await uow.users.get_uid(ctx.sender_id)
            shop = await build_xjshop(uow)
            user = UserData(
                uid=uid, qqid=str(ctx.sender_id), name=await ctx.sender_name
            )
            freezed_shop = await shop.freeze(uow, uid)
            money = await uow.money.get(uid)
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
            remain = await uow.money.use(uid, costs)
            print(prods)
        await ctx.send(await shop_buy_message(user, prods, costs, remain))
