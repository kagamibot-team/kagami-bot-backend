import qrcode
import qrcode.main
import qrcode.constants
import PIL.Image
from src.common.fast_import import *


async def send_shop_message(ctx: OnebotContext, shop: ShopData):
    boxes: list[PILImage] = []

    for group, products in shop.products.items():
        boxes.append(
            await drawASingleLineClassic(
                group, "#FFFFFF", Fonts.HARMONYOS_SANS_BLACK, 60
            )
        )

        subs: list[PILImage] = []
        for product in products:
            subs.append(await product_box(product))
        boxes.append(
            await combineABunchOfImage(0, 0, subs, 3, "#9B9690", "center", "left", marginBottom=30)
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
async def _(ctx: OnebotContext, session: AsyncSession, res: Arparma):
    buys = res.query[list[str]]("商品名列表")
    uid = await get_uid_by_qqid(session, ctx.getSenderId())
    shop_data = ShopData({})
    shop_data_evt = ShopBuildingEvent(shop_data, ctx.getSenderId(), uid, session)
    await root.emit(shop_data_evt)

    if buys is None:
        await send_shop_message(ctx, shop_data)
        return

    buy_result = "小镜的 Shop 销售小票\n"
    buy_result += "--------------------\n"
    buy_result += f"日期：{now_datetime().strftime('%Y-%m-%d')}\n"
    buy_result += f"时间：{now_datetime().strftime('%H:%M:%S')}\n"
    buy_result += f"客户：{await ctx.getSenderName()}\n"
    buy_result += f"编号：{ctx.getSenderId()}\n"
    buy_result += "--------------------\n\n"

    money_left_query = select(User.money).filter(User.data_id == uid)
    money_left = (await session.execute(money_left_query)).scalar_one()

    money_sum = 0.0
    products: list[ProductData] = []

    for buy in buys:
        for products in shop_data.products.values():
            for product in products:
                if buy == product.title or buy in product.alias:
                    if product.sold_out:
                        buy_result += f"- {product.title} 已售罄\n"
                        continue

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

    await session.commit()

    buy_result += "\n"
    buy_result += f"总计：{money_sum}{la.unit.money}\n"

    if money_sum > money_left:
        buy_result += f"实付：0.00{la.unit.money}\n"
        buy_result += f"余额：{money_left}{la.unit.money}\n"
        buy_result += "--------------------\n"
        buy_result += "  购买失败，余额不足\n"
        buy_result += "  欢迎下次光临\n"
        buy_result += "--------------------\n"
    else:
        buy_result += f"实付：{money_sum}{la.unit.money}\n"
        buy_result += f"余额：{money_left - money_sum}{la.unit.money}\n"
        buy_result += "--------------------\n"
        buy_result += "  本次消费已结帐\n"
        buy_result += "  欢迎下次光临\n"
        buy_result += "--------------------\n"

    image = await drawLimitedBoxOfTextClassic(
        text=buy_result,
        maxWidth=336,
        color="#000000",
        lineHeight=28,
        font=Fonts.VONWAON_BITMAP_12,
        fontSize=24,
        expandTop=60,
        expandBottom=220,
        align=HorizontalAnchor.left,
        expandLeft=20,
        expandRight=20,
    )

    base = PIL.Image.new("RGB", image.size, "#FFFFFF")
    base.paste(image, (0, 0), image)

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
