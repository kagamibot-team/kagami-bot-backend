import qrcode
import qrcode.main
import qrcode.constants
import PIL.Image
from src.imports import *


async def send_shop_message(ctx: OnebotMessageContext, shop: ShopData):
    boxes: list[PILImage] = []

    for group, products in shop.products.items():
        boxes.append(
            await getTextImage(
                text=group,
                color="#FFFFFF",
                font=Fonts.HARMONYOS_SANS_BLACK,
                font_size=60,
            )
        )

        subs: list[PILImage] = []
        for product in products:
            subs.append(await product_box(product))
        boxes.append(
            await pileImages(
                images=subs,
                rowMaxNumber=3,
                background="#9B9690",
                horizontalAlign="center",
                marginBottom=30,
            )
        )

    image = await verticalPile(boxes, 0, "left", "#9B9690", 484, 80, 80, 80)
    image.paste(PIL.Image.open("./res/kagami_shop.png"), (0, 0))
    await ctx.reply(
        "输入“小镜商店 购买 商品名”就可以购买了"
        + UniMessage.image(raw=imageToBytes(image))
    )


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
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession, res: Arparma):
    buys = res.query[list[str]]("商品名列表")
    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    shop_data = ShopData()
    shop_data_evt = ShopBuildingEvent(shop_data, ctx.getSenderId(), uid, session)
    await root.emit(shop_data_evt)

    if buys is None:
        await send_shop_message(ctx, shop_data)
        return

    name = await ctx.getSenderName()

    if isinstance(ctx, GroupContext):
        name = await ctx.getSenderNameInGroup()

    buy_result = "小镜的 Shop 销售小票\n"
    buy_result += "--------------------\n"
    buy_result += f"日期：{now_datetime().strftime('%Y-%m-%d')}\n"
    buy_result += f"时间：{now_datetime().strftime('%H:%M:%S')}\n"
    buy_result += f"客户：{name}\n"
    buy_result += f"编号：{ctx.getSenderId()}\n"
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
            evt = ShopBuyEvent(product, ctx.getSenderId(), uid, session)
            await root.emit(evt)

        money_update_query = (
            update(User).where(User.data_id == uid).values(money=money_left - money_sum)
        )
        await session.execute(money_update_query)

    await session.commit()

    buy_result += "\n"
    buy_result += f"总计：{money_sum}{la.unit.money}\n"

    if money_sum > money_left:
        await ctx.reply("你什么也没买到……因为你薯片不够了")
        return
    elif money_sum == 0:
        await ctx.reply("你什么也没买到……小镜找不到你要买的东西，或者它们都卖光了")
        return
    else:
        buy_result += f"实付：{money_sum}{la.unit.money}\n"
        buy_result += f"余额：{money_left - money_sum}{la.unit.money}\n"
        buy_result += "--------------------\n"
        buy_result += "  本次消费已结帐\n"
        buy_result += "  欢迎下次光临\n"
        buy_result += "--------------------\n"

    image = await getTextImage(
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
    await imagePaste(base, image, 0, 0)

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

    await ctx.send(UniMessage.image(raw=imageToBytes(base)))
