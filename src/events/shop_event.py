from src.imports import *
from src.logic.catch_time import calculateTime


@root.listen(ShopBuildingEvent)
async def _(e: ShopBuildingEvent):
    """增加卡槽上限的商品"""

    userTime = await calculateTime(e.session, e.uid)
    catchMax = userTime.pickMax + 1
    pd = ProductData(
        image="./res/add1.png",
        title=f"增加卡槽上限",
        description="增加卡槽上限至%d" % catchMax,
        price=25 * (2 ** (catchMax - 1)),
        sold_out=False,
        alias=["加上限", "增加上限", "增加卡槽上限", "增加上限至%d" % catchMax],
        background_color="#9e9d95",
    )
    if not "道具" in e.data.products.keys():
        e.data.products["道具"] = []
    e.data.products["道具"].append(pd)


@root.listen(ShopBuyEvent)
async def _(e: ShopBuyEvent):
    """更改卡槽上限"""

    if e.product.title == "增加卡槽上限":
        await e.session.execute(
            update(User)
            .where(User.data_id == e.uid)
            .values(
                pick_max_cache=User.pick_max_cache + 1,
            )
        )


@root.listen(ShopBuildingEvent)
async def _(e: ShopBuildingEvent):
    """增加小哥皮肤商品"""

    query = (
        select(
            Skin.name,
            Skin.price,
            Skin.image,
            Award.name,
            Level.color_code,
        )
        .filter(Skin.price > 0)
        .join(Award, Award.data_id == Skin.applied_award_id)
        .join(Level, Level.data_id == Award.level_id)
    )
    skins = (await e.session.execute(query)).tuples().all()

    query = (
        select(Skin.name)
        .join(OwnedSkin, OwnedSkin.skin_id == Skin.data_id)
        .filter(OwnedSkin.user_id == e.uid)
    )
    owned = (await e.session.execute(query)).scalars().all()

    for name, price, image, aname, color in skins:
        pd = ProductData(
            image=await blurred(image, 100),
            title=f"皮肤{name}",
            description=f"{aname}",
            price=price,
            sold_out=name in owned,
            alias=[],
            background_color=color,
        )
        if not "皮肤" in e.data.products.keys():
            e.data.products["皮肤"] = []
        e.data.products["皮肤"].append(pd)


@root.listen(ShopBuyEvent)
async def _(e: ShopBuyEvent):
    """购买皮肤"""

    if e.product.title.startswith("皮肤"):
        name = e.product.title.split("皮肤")[1]
        query = select(Skin.data_id).filter(Skin.name == name)
        skin_id = (await e.session.execute(query)).scalar_one()

        await e.session.execute(
            insert(OwnedSkin).values(user_id=e.uid, skin_id=skin_id)
        )
