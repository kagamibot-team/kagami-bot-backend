from typing import Any

import PIL.Image
import qrcode
import qrcode.constants
import qrcode.main
from arclet.alconna import Alconna, Arg, Arparma, MultiVar, Option
from nonebot_plugin_alconna import UniMessage
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.command_events import GroupContext, OnebotContext
from src.base.event_root import root
from src.common.data.users import get_uid_by_qqid
from src.common.dataclasses.shop_data import (
    ProductData,
    ShopBuildingEvent,
    ShopBuyEvent,
    ShopData,
)
from src.common.decorators.command_decorators import (
    listenOnebot,
    matchAlconna,
    withLoading,
)
from src.common.lang.zh import la
from src.common.times import now_datetime
from src.core.unit_of_work import get_unit_of_work
from src.models.models import User
from src.ui.base.basics import Fonts, paste_image, pile, render_text, vertical_pile
from src.ui.base.tools import image_to_bytes
from src.ui.deprecated.product import product_box


async def send_shop_message(ctx: OnebotContext, session: AsyncSession, shop: ShopData):
    titles: list[PIL.Image.Image] = []
    boxes: list[PIL.Image.Image] = []

    name = await ctx.getSenderName()
    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderName()

    res = await session.execute(select(User.money).filter(User.qq_id == ctx.sender_id))
    res = res.scalar_one_or_none() or 0.0

    titles.append(
        render_text(
            text=(
                f"欢迎来到小镜商店，{name}！您拥有{int(res)}{la.unit.money}。\n"
                "输入“小镜商店 购买 {商品名}”就可以购买了。\n"
            ),
            width=808 - 80 * 2,
            color="#FFFFFF",
            font=Fonts.HARMONYOS_SANS_BLACK,
            font_size=28,
        )
    )

    for group, products in shop.products.items():
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
    await ctx.send(UniMessage.image(raw=image_to_bytes(image)))


@listenOnebot()
@matchAlconna(
    Alconna(
        "re:(小镜的?|xj) ?(shop|小店|商店)",
        Option(
            "买",
            alias=["购买", "购入", "buy"],
            args=Arg("商品名列表", MultiVar(str, flag="+")),
        ),
    )
)
@withLoading()
async def _(ctx: OnebotContext, res: Arparma[Any]):
    buys = res.query[list[str]]("商品名列表")

    async with get_unit_of_work(ctx.sender_id) as uow:
        session = uow.session
        uid = await get_uid_by_qqid(session, ctx.sender_id)
        shop_data = ShopData()
        shop_data_evt = ShopBuildingEvent(shop_data, ctx.sender_id, uid, session)
        await root.emit(shop_data_evt)

        if buys is None:
            await send_shop_message(ctx, session, shop_data)
            return

        name = await ctx.getSenderName()

        if isinstance(ctx, GroupContext):
            name = await ctx.getSenderName()

        buy_result = "小镜的 Shop 销售小票\n"
        buy_result += "--------------------\n"
        buy_result += f"日期：{now_datetime().strftime('%Y-%m-%d')}\n"
        buy_result += f"时间：{now_datetime().strftime('%H:%M:%S')}\n"
        buy_result += f"客户：{name}\n"
        buy_result += f"编号：{ctx.sender_id}\n"
        buy_result += "--------------------\n\n"

        money_left_query = select(User.money).filter(User.data_id == uid)
        money_left = (await session.execute(money_left_query)).scalar_one()

        money_sum = 0.0
        products: list[ProductData] = []

        for buy in set(buys):
            for product in shop_data.iterate():
                if buy == product.title or buy in product.alias:
                    if product.sold_out:
                        buy_result += f"- {product.title} 已售罄\n"
                        break

                    buy_result += f"- {product.title} {product.price}{la.unit.money}\n"
                    money_sum += product.price
                    products.append(product)
                    break
            else:
                buy_result += f"- {buy} 未找到\n"
                continue

        if money_sum <= money_left:
            for product in products:
                evt = ShopBuyEvent(product, ctx.sender_id, uid, session)
                await root.emit(evt)

            money_update_query = (
                update(User)
                .where(User.data_id == uid)
                .values(money=money_left - money_sum)
            )
            await session.execute(money_update_query)

    buy_result += "\n"
    buy_result += f"总计：{money_sum}{la.unit.money}\n"

    if money_sum > money_left:
        await ctx.reply("你什么也没买到……因为你薯片不够了")
        return

    if money_sum == 0:
        await ctx.reply("你什么也没买到……小镜找不到你要买的东西，或者它们都卖光了")
        return

    buy_result += f"实付：{money_sum}{la.unit.money}\n"
    buy_result += f"余额：{money_left - money_sum}{la.unit.money}\n"
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

    base = PIL.Image.new("RGB", image.size, "#FFFFFF")
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

    await ctx.send(UniMessage.image(raw=image_to_bytes(base)))
