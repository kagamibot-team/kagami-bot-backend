"""
对小哥进行的增删查改操作
"""

from src.common.fast_import import *


@listenPublic()
@requireAdmin()
@matchAlconna(
    Alconna(
        "小哥",
        ["::添加", "::创建"],
        Arg("name", str),
        Arg("level", str),
    )
)
async def _(ctx: PublicContext, res: Arparma):
    name = res.query[str]("name")
    levelName = res.query[str]("level")

    assert name is not None
    assert levelName is not None

    session = get_session()

    async with session.begin():
        _award = (
            await session.execute(select(Award.data_id).filter(Award.name == name))
        ).scalar_one_or_none()

        if _award is None:
            _award = (await session.execute(
                select(Award.data_id).filter(
                    Award.alt_names.any(AwardAltName.name == name)
                )
            )).scalar_one_or_none()

        if _award is not None:
            await ctx.reply(UniMessage(f"名字叫 {name} 的小哥已存在。"))
            return

        level = (
            await session.execute(select(Level.data_id).filter(Level.name == levelName))
        ).scalar_one_or_none()

        if level is None:
            level = (
                await session.execute(
                    select(Level.data_id).filter(
                        Level.alt_names.any(LevelAltName.name == levelName)
                    )
                )
            ).scalar_one_or_none()

        if level is None:
            await ctx.reply(UniMessage(f"等级 {levelName} 不存在。"))
            return

        award = Award(level_id=level, name=name)
        session.add(award)
        await session.commit()

        await ctx.reply(UniMessage(f"成功创建名字叫 {name} 的小哥。"))


@listenPublic()
@requireAdmin()
@matchAlconna(
    Alconna(
        "小哥",
        ["::删除", "::移除"],
        Arg("name", str),
    )
)
async def _(ctx: PublicContext, res: Arparma):
    name = res.query[str]("name")

    assert name is not None

    session = get_session()

    async with session.begin():
        await session.execute(
            delete(Award).filter(Award.name == name)
        )
        await session.execute(
            delete(Award).filter(Award.alt_names.any(
                AwardAltName.name == name
            ))
        )
        await session.commit()
        await ctx.reply(UniMessage(f"成功删除名字叫 {name} 的小哥。"))


@listenPublic()
@requireAdmin()
@withAlconna(
    Alconna(
        "re:(修改|更改|调整|改变)小哥",
        ["::"],
        Arg("小哥原名", str),
        Option("名字", Arg("小哥新名字", str), alias=["--name", "名称", "-n", "-N"], compact=True),
        Option("等级", Arg("等级名字", str), alias=["--level", "级别", "-l", "-L"], compact=True),
        Option("描述", Arg("描述", MultiVar(str, flag='+'), seps="\n"), alias=["--description", "-d", "-D"], compact=True),
        Option("图片", Arg("图片", Image), alias=["--image", "照片", "-i", "-I"])
    )
)
@withFreeSession()
async def _(session: AsyncSession, ctx: PublicContext, res: Arparma):
    if res.error_info is not None and isinstance(res.error_info, ArgumentMissing):
        await ctx.reply(UniMessage(repr(res.error_info)))
        return
    
    # if res.error_info is not None and isinstance(res.error_info, InvalidParam):
    #     await ctx.reply(UniMessage(repr(res.error_info)))
    #     return
    
    if not res.matched:
        return

    name = res.query[str]("小哥原名")

    if name is None:
        return
    
    aid = await getAidByName(session, name)

    if aid is None:
        await ctx.reply(UniMessage(f"名字叫 {name} 的小哥不存在。"))
        return

    newName = res.query[str]("名字")
    levelName = res.query[str]("等级名字")
    _description = res.query[tuple[str]]("描述")
    image = res.query[Image]("图片")

    messages = UniMessage() + "本次更改结果：\n\n"

    if newName is not None:
        await session.execute(
            update(Award).where(Award.data_id == aid).values(name=newName)
        )
        messages += f"成功将名字叫 {name} 的小哥的名字改为 {newName}。\n"
    
    if levelName is not None:
        lid = await getLidByName(session, levelName)
        
        if lid is None:
            messages += f"更改等级未成功，因为名字叫 {levelName} 的等级不存在。"
        else:
            await session.execute(
                update(Award).where(Award.data_id == aid).values(level_id=lid)
            )
            messages += f"成功将名字叫 {name} 的小哥的等级改为 {levelName}。\n"
    
    if _description is not None:
        description = "\n".join(_description)
        await session.execute(
            update(Award).where(Award.data_id == aid).values(description=description)
        )
        messages += f"成功将名字叫 {name} 的小哥的描述改为 {description}。\n"
    
    if image is not None:
        imageUrl = image.url
        if imageUrl is None:
            logger.warning(f"名字叫 {name} 的小哥的图片地址为空。")
        else:
            try:
                fp = await downloadAwardImage(aid, imageUrl)
                await session.execute(
                    update(Award).where(Award.data_id == aid).values(img_path=fp)
                )
                messages += f"成功将名字叫 {name} 的小哥的图片改为 {fp}。\n"
            except Exception as e:
                logger.warning(f"名字叫 {name} 的小哥的图片下载失败。")
                logger.exception(e)
    
    await ctx.reply(messages)
