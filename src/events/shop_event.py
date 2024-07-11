from src.imports import *
from src.logic.catch_time import calculateTime


@root.listen(ShopBuildingEvent)
async def _(e: ShopBuildingEvent):
    """增加卡槽上限的商品"""

    userTime = await calculateTime(e.session, e.uid)
    catchMax = userTime.pickMax + 1
    pd = ProductData(
        image="./res/add1.png",
        title="增加卡槽上限",
        description=f"增加卡槽上限至{catchMax}",
        price=25 * (2 ** (catchMax - 1)),
        sold_out=False,
        alias=["加上限", "增加上限", "增加卡槽上限", f"增加上限至{catchMax}"],
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
    """小哥合成器凭证"""

    u = await do_user_have_flag(e.session, e.uid, "合成")
    pd = ProductData(
        image="./res/merge_machine.png",
        title="小哥合成凭证",
        description="购买合成小哥机器的使用权",
        price=1200,
        sold_out=u,
        alias=["合成小哥凭证", "合成凭证", "合成"],
        background_color="#9e9d95",
    )
    e.data.push(pd, "道具")


@root.listen(ShopBuyEvent)
async def _(e: ShopBuyEvent):
    """小哥合成器凭证"""

    if e.product.title == "小哥合成凭证":
        await add_user_flag(e.session, e.uid, "合成")


@root.listen(ShopBuildingEvent)
async def _(e: ShopBuildingEvent):
    """增加小哥皮肤商品"""

    query = (
        select(
            Skin.name,
            Skin.price,
            Skin.image,
            Award.name,
            Award.level_id,
        )
        .filter(Skin.price > 0)
        .join(Award, Award.data_id == Skin.award_id)
    )
    skins = (await e.session.execute(query)).tuples().all()

    query = (
        select(Skin.name)
        .join(SkinRecord, SkinRecord.skin_id == Skin.data_id)
        .filter(SkinRecord.user_id == e.uid)
    )
    owned = (await e.session.execute(query)).scalars().all()

    for name, price, image, aname, lid in skins:
        pd = ProductData(
            image=await blurred(image, 100),
            title=f"皮肤{name}",
            description=f"{aname}",
            price=price,
            sold_out=name in owned,
            alias=[],
            background_color=level_repo.levels[lid].color,
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
            insert(SkinRecord).values(user_id=e.uid, skin_id=skin_id)
        )
