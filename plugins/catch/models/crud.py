"""
`curd` 模块主要用于数据库的增、删、查、改。任何逻辑都不应该在这里实现。
"""

from re import L
from sqlalchemy import delete, select
from nonebot_plugin_orm import AsyncSession, async_scoped_session

from .models import *


Session = async_scoped_session | AsyncSession


### GLOBAL ###
async def getGlobal(session: Session):
    "返回全局变量"

    glob = (await session.execute(select(Global))).scalar_one_or_none()

    if glob is None:
        glob = Global()
        session.add(glob)
        await session.flush()

    return glob


async def deleteObj(session: Session, obj: object):
    "删除对象"

    if obj is None:
        return

    await session.delete(obj)
    await session.flush()


### TAG ###


async def getTag(session: Session, tag_name: str, tag_args: str):
    "根据名字和属性返回标签，如果不存在则立即创建"

    tag = (
        await session.execute(
            select(Tag).filter(Tag.tag_name == tag_name, Tag.tag_args == tag_args)
        )
    ).scalar_one_or_none()

    if tag is None:
        tag = Tag(tag_name, tag_args)
        session.add(tag)
        await session.flush()

    return tag


### LEVEL ###
async def getAllLevels(session: Session):
    "返回所有拥有小哥的等级的列表"

    return (
        (
            await session.execute(
                select(Level)
                .filter(Level.awards.any())
                .order_by(-Level.sorting_priority, Level.weight)
            )
        )
        .scalars()
        .all()
    )


async def getLevelByName(session: Session, name: str):
    "根据名字返回等级，如果不存在则返回 None"

    level = (
        await session.execute(select(Level).filter(Level.name == name))
    ).scalar_one_or_none()

    if level is None:
        levelAlt = (
            await session.execute(
                select(LevelAltName).filter(LevelAltName.name == name)
            )
        ).scalar_one_or_none()
        if levelAlt is not None:
            level = levelAlt.level

    return level


async def createLevelAltName(session: Session, level: Level, name: str):
    "创建一个等级的别名，返回是否创建成功"

    _l = await getLevelByName(session, name)

    if _l is not None:
        return False

    alt = LevelAltName(level, name)
    session.add(alt)
    await session.flush()

    return True


async def getLevelAltNameObject(session: Session, name: str):
    "根据名字返回等级的别名，如果不存在则返回 None"

    return (
        await session.execute(select(LevelAltName).filter(LevelAltName.name == name))
    ).scalar_one_or_none()


async def getLevelTags(session: Session, level: Level):
    "返回等级的所有标签"

    relations = await session.execute(
        select(LevelTagRelation.tag).filter(LevelTagRelation.level == level)
    )

    return relations.scalars().all()


async def getLevelTag(session: Session, level: Level, tag: Tag):
    "判断等级是否拥有标签"

    return (
        await session.execute(
            select(LevelTagRelation).filter(
                LevelTagRelation.level == level, LevelTagRelation.tag == tag
            )
        )
    ).scalar_one_or_none()


async def addLevelTag(session: Session, level: Level, tag: Tag):
    "为等级添加标签"

    if await getLevelTag(session, level, tag) is None:
        relation = LevelTagRelation(level, tag)
        session.add(relation)
        await session.flush()


async def removeLevelTag(session: Session, level: Level, tag: Tag):
    "为等级移除标签"

    relation = await getLevelTag(session, level, tag)
    if relation is not None:
        await session.delete(relation)
        await session.flush()


### AWARD ###
async def getAllAwards(session: Session):
    "返回所有有可能被抓到的小哥"

    return (
        (
            await session.execute(
                select(Award).join(Level, Award.level).filter(Level.weight > 0)
            )
        )
        .scalars()
        .all()
    )


async def getAllAwardsInLevel(session: Session, level: Level):
    "返回某一等级所有的小哥，以添加顺序排序"

    return (
        (
            await session.execute(
                select(Award).filter(Award.level == level).order_by(Award.data_id)
            )
        )
        .scalars()
        .all()
    )


async def getAwardById(session: Session, id: int):
    "根据 ID 返回小哥，如果不存在会报错"

    return await session.get_one(Award, id)


async def getAwardByName(session: Session, name: str):
    "根据名字返回小哥，如果不存在则返回 None"

    award = (
        await session.execute(select(Award).filter(Award.name == name))
    ).scalar_one_or_none()

    if award is None:
        awardAlt = (
            await session.execute(
                select(AwardAltName).filter(AwardAltName.name == name)
            )
        ).scalar_one_or_none()
        if awardAlt is not None:
            award = awardAlt.award

    return award


async def createAwardAltName(session: Session, award: Award, name: str):
    "创建一个小哥的别名，返回是否创建成功"

    _a = await getAwardByName(session, name)

    if _a is not None:
        return False

    alt = AwardAltName(award, name)
    session.add(alt)
    await session.flush()

    return True


async def getAwardAltNameObject(session: Session, name: str):
    "根据名字返回小哥的别名，如果不存在则返回 None"

    return (
        await session.execute(select(AwardAltName).filter(AwardAltName.name == name))
    ).scalar_one_or_none()


async def getAwardTags(session: Session, award: Award):
    "返回小哥的所有标签"

    relations = await session.execute(
        select(AwardTagRelation.tag).filter(AwardTagRelation.award == award)
    )

    return relations.scalars().all()


async def getAwardTag(session: Session, award: Award, tag: Tag):
    "判断小哥是否拥有标签"

    return (
        await session.execute(
            select(AwardTagRelation).filter(
                AwardTagRelation.award == award, AwardTagRelation.tag == tag
            )
        )
    ).scalar_one_or_none()


async def addAwardTag(session: Session, award: Award, tag: Tag):
    "为小哥添加标签"

    if await getAwardTag(session, award, tag) is None:
        relation = AwardTagRelation(award, tag)
        session.add(relation)
        await session.flush()


async def removeAwardTag(session: Session, award: Award, tag: Tag):
    "为小哥移除标签"

    relation = await getAwardTag(session, award, tag)
    if relation is not None:
        await session.delete(relation)
        await session.flush()


async def removeAward(session: Session, award: Award):
    "移除一个小哥"

    # 移除于它绑定的所有别名
    await session.execute(
        delete(AwardAltName).filter(AwardAltName.award == award)
    )
    # 移除于它绑定的所有标签
    await session.execute(
        delete(AwardTagRelation).filter(AwardTagRelation.award == award)
    )
    # 移除于它绑定的所有统计
    await session.execute(
        delete(StorageStats).filter(StorageStats.award == award)
    )
    await session.execute(
        delete(UsedStats).filter(UsedStats.award == award)
    )
    # 删除与它有关的全部皮肤
    await session.execute(
        delete(Skin).filter(Skin.award == award)
    )
    # 移除它本身
    await session.delete(award)
    await session.flush()


### USER ###
async def getUser(session: Session, qqid: int):
    "返回一个用户，如果该用户不存在，则立即创建"

    userResult = await session.execute(select(User).filter(User.qq_id == qqid))

    user = userResult.scalar_one_or_none()

    if user is None:
        user = User(qq_id=qqid)
        session.add(user)
        await session.flush()

    return user


async def getUserById(session: Session, id: int):
    "根据 ID 返回用户，如果不存在则报错"

    return await session.get_one(User, id)


async def getStorage(session: Session, user: User, award: Award):
    "返回一个用户的小哥库存，如果没有，则立即创建"

    stats = (
        await session.execute(
            select(StorageStats)
            .filter(StorageStats.user == user)
            .filter(StorageStats.award == award)
        )
    ).scalar_one_or_none()

    if not stats:
        stats = StorageStats(user, award, 0)
        session.add(stats)
        await session.flush()

    return stats


async def getUsed(session: Session, user: User, award: Award):
    "返回一个用户的已消耗小哥的统计，如果没有，则立即创建"

    stats = (
        await session.execute(
            select(UsedStats)
            .filter(UsedStats.user == user)
            .filter(UsedStats.award == award)
        )
    ).scalar_one_or_none()

    if not stats:
        stats = UsedStats(user, award, 0)
        session.add(stats)
        await session.flush()

    return stats


async def clearUserStorage(session: Session, user: User, award: Award | None = None):
    "清空用户的小哥库存"

    if award is None:
        await session.execute(delete(StorageStats).where(StorageStats.user == user))
        await session.execute(delete(UsedStats).where(UsedStats.user == user))
    else:
        await session.execute(
            delete(StorageStats).where(
                (StorageStats.user == user) & (StorageStats.award == award)
            )
        )
        await session.execute(
            delete(UsedStats).where(
                (UsedStats.user == user) & (UsedStats.award == award)
            )
        )

    await session.flush()


### SKIN ###
async def getAllSkins(session: Session):
    "返回所有皮肤"

    return (await session.execute(select(Skin))).scalars().all()


async def getAllSkinsSelling(session: Session):
    "返回所有价格大于 0 的皮肤"

    return (await session.execute(select(Skin).filter(Skin.price > 0))).scalars().all()


async def getSkinByName(session: Session, name: str):
    "根据名字返回皮肤，如果没有则返回 None"

    skin = (
        await session.execute(select(Skin).filter(Skin.name == name))
    ).scalar_one_or_none()

    if skin is None:
        skinAlt = (
            await session.execute(select(SkinAltName).filter(SkinAltName.name == name))
        ).scalar_one_or_none()
        if skinAlt is not None:
            skin = skinAlt.skin

    return skin


async def getSkinById(session: Session, id: int):
    "根据 ID 返回皮肤，如果不存在则报错"

    return await session.get_one(Skin, id)


async def createSkinAltName(session: Session, skin: Skin, name: str):
    "创建一个皮肤的别名，返回是否创建成功"

    _s = await getSkinByName(session, name)

    if _s is not None:
        return False

    alt = SkinAltName(skin, name)
    session.add(alt)
    await session.flush()

    return True


async def getSkinAltNameObject(session: Session, name: str):
    "根据名字返回皮肤的别名，如果不存在则返回 None"

    return (
        await session.execute(select(SkinAltName).filter(SkinAltName.name == name))
    ).scalar_one_or_none()


async def getUsedSkin(session: Session, user: User, award: Award) -> UsedSkin | None:
    "返回皮肤使用记录"

    return (
        await session.execute(
            select(UsedSkin)
            .filter(UsedSkin.user == user)
            .join(Skin, UsedSkin.skin)
            .filter(Skin.award == award)
        )
    ).scalar_one_or_none()


async def setSkin(session: Session, user: User, skin: Skin):
    "设置用户的皮肤"

    us = await getUsedSkin(session, user, skin.award)

    if us:
        us.skin = skin
    else:
        session.add(UsedSkin(user, skin))

    await session.flush()
    return


async def getAwardImage(session: Session, user: User, award: Award) -> str:
    "返回用户限定的小哥图片"

    record = await getUsedSkin(session, user, award)

    if record == None:
        return award.img_path

    return record.skin.image


async def getAwardDescription(session: Session, user: User, award: Award) -> str:
    "返回用户限定的小哥描述"

    record = await getUsedSkin(session, user, award)

    if record == None or record.skin.extra_description == "":
        return award.description

    return record.skin.extra_description


async def getOwnedSkin(session: Session, user: User, skin: Skin) -> OwnedSkin | None:
    "返回用户拥有皮肤的记录，如果没有则为 `None`"

    return (
        await session.execute(
            select(OwnedSkin)
            .filter(OwnedSkin.user == user)
            .filter(OwnedSkin.skin == skin)
        )
    ).scalar_one_or_none()


async def getAllOwnedSkin(session: Session, user: User, award: Award):
    "返回用户拥有皮肤的记录"

    return (
        (
            await session.execute(
                select(OwnedSkin)
                .filter(OwnedSkin.user == user)
                .filter(OwnedSkin.skin.has(award=award))
            )
        )
        .scalars()
        .all()
    )


async def getSkinTags(session: Session, skin: Skin):
    "返回皮肤的标签"

    return await session.execute(
        select(SkinTagRelation.tag).filter(SkinTagRelation.skin == skin)
    )


async def getSkinTag(session: Session, skin: Skin, tag: Tag):
    "返回皮肤的一个标签关系，如果不存在则为 `None`"

    return (
        await session.execute(
            select(SkinTagRelation)
            .filter(SkinTagRelation.skin == skin)
            .filter(SkinTagRelation.tag == tag)
        )
    ).scalar_one_or_none()


async def addSkinTag(session: Session, skin: Skin, tag: Tag):
    "添加一个皮肤标签关系"

    if await getSkinTag(session, skin, tag) == None:
        session.add(SkinTagRelation(skin, tag))
        await session.flush()


async def removeSkinTag(session: Session, skin: Skin, tag: Tag):
    "删除一个皮肤标签关系"

    if (rel := await getSkinTag(session, skin, tag)) != None:
        await session.delete(rel)
        await session.flush()


__all__ = [
    "getGlobal",
    "getAllLevels",
    "getAllAwards",
    "getAllAwardsInLevel",
    "getAwardById",
    "getUser",
    "getUserById",
    "getStorage",
    "getUsed",
    "getAllSkins",
    "getAllSkinsSelling",
    "getSkinByName",
    "getUsedSkin",
    "setSkin",
    "getAwardImage",
    "getAwardDescription",
    "getOwnedSkin",
    "createSkinAltName",
    "createLevelAltName",
    "createAwardAltName",
    "getAwardByName",
    "getLevelByName",
    "getLevelAltNameObject",
    "getAwardAltNameObject",
    "getSkinAltNameObject",
    "getAllOwnedSkin",
    "clearUserStorage",
    "deleteObj",
    "getSkinById",
    "getTag",
    "getLevelTags",
    "getLevelTag",
    "addLevelTag",
    "removeLevelTag",
    "getAwardTags",
    "getAwardTag",
    "addAwardTag",
    "removeAwardTag",
    "getSkinTags",
    "getSkinTag",
    "addSkinTag",
    "removeSkinTag",
    "removeAward"
]
