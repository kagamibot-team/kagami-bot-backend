from src.common.fast_import import *
from src.components.ref_book import skin_book


@dataclass
class SkinInfo:
    aName: str
    name: str
    image: str
    extra_description: str
    price: float


@listenPublic()
@requireAdmin()
@matchAlconna(
    Alconna(
        ["::"],
        "re:(所有|全部)皮肤",
        Arg("name", str, flags=[ArgFlag.OPTIONAL]),
    )
)
@withLoading()
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    name = res.query[str]("name")

    query = (
        select(Skin.name, Award.name, Skin.price, Level.color_code, Skin.image)
        .join(Award, Skin.applied_award_id == Award.data_id)
        .join(Level, Level.data_id == Award.level_id)
        .order_by(-Level.sorting_priority, Level.weight, Skin.applied_award_id)
    )

    if name:
        query1 = query.filter(Award.name == name)
        query2 = query.filter(Skin.name == name)
        query3 = query.filter(Award.alt_names.any(AwardAltName.name == name))
        query4 = query.filter(Skin.alt_names.any(SkinAltName.name == name))

        skins1 = (await session.execute(query1)).tuples()
        skins2 = (await session.execute(query2)).tuples()
        skins3 = (await session.execute(query3)).tuples()
        skins4 = (await session.execute(query4)).tuples()

        skins = list(skins1) + list(skins2) + list(skins3) + list(skins4)
    else:
        skins = list((await session.execute(query)).tuples())

    boxes: list[PILImage] = []
    for box in skins:
        boxes.append(await skin_book(box[0], box[1], str(box[2]), box[3], box[4]))

    imgout = await combineABunchOfImage(
        paddingX=0,
        paddingY=0,
        images=boxes,
        rowMaxNumber=6,
        background="#9B9690",
        horizontalAlign="top",
        verticalAlign="left",
        marginLeft=30,
        marginRight=30,
        marginBottom=30,
        marginTop=30,
    )

    await ctx.send(UniMessage().image(raw=imageToBytes(imgout)))


@listenPublic()
@requireAdmin()
@withAlconna(
    Alconna(
        "re:(修改|更改|调整|改变|设置|设定)皮肤",
        ["::"],
        Arg("皮肤原名", str),
        Option(
            "名字",
            Arg("皮肤新名字", str),
            alias=["--name", "名称", "-n", "-N"],
            compact=True,
        ),
        Option(
            "描述",
            Arg("描述", MultiVar(str, flag="*"), seps="\n"),
            alias=["--description", "-d", "-D"],
            compact=True,
        ),
        Option("图片", Arg("图片", Image), alias=["--image", "照片", "-i", "-I"]),
        Option(
            "价格", Arg("价格", float), alias=["--price", "价钱", "售价", "-p", "-P"]
        ),
    )
)
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    if res.error_info is not None and isinstance(res.error_info, ArgumentMissing):
        await ctx.reply(UniMessage(repr(res.error_info)))
        return

    if not res.matched:
        return

    name = res.query[str]("皮肤原名")

    if name is None:
        return

    sid = await get_sid_by_name(session, name)

    if sid is None:
        await ctx.reply(UniMessage(f"名字叫 {name} 的皮肤不存在。"))
        return

    newName = res.query[str]("皮肤新名字")
    price = res.query[float]("价格")
    _description = res.query[tuple[str]]("描述")
    image = res.query[Image]("图片")

    messages = UniMessage() + "本次更改结果：\n\n"

    if newName is not None:
        await session.execute(
            update(Skin).where(Skin.data_id == sid).values(name=newName)
        )
        messages += f"成功将名字叫 {name} 的皮肤的名字改为 {newName}。\n"

    if price is not None:
        await session.execute(
            update(Skin).where(Skin.data_id == sid).values(price=price)
        )
        messages += f"成功将名字叫 {name} 的皮肤的价格改为 {price}。\n"

    if _description is not None:
        description = "\n".join(_description)
        await session.execute(
            update(Skin)
            .where(Skin.data_id == sid)
            .values(extra_description=description)
        )
        messages += f"成功将名字叫 {name} 的皮肤的描述改为 {description}\n"

    if image is not None:
        imageUrl = image.url
        if imageUrl is None:
            logger.warning(f"名字叫 {name} 的皮肤的图片地址为空。")
        else:
            try:
                fp = await downloadSkinImage(sid, imageUrl)
                await session.execute(
                    update(Skin).where(Skin.data_id == sid).values(image=fp)
                )
                messages += f"成功将名字叫 {name} 的皮肤的图片改为 {fp}。\n"
            except Exception as e:
                logger.warning(f"名字叫 {name} 的皮肤的图片下载失败。")
                logger.exception(e)

    await ctx.reply(messages)
