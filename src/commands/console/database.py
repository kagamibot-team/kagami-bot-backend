"""
所有仅在控制台中才能使用的指令
"""

import asyncio
import os
import pickle
import time
import tarfile

from src.imports import *


to_pickle_list: list[type[Base]] = [
    Global,
    Level,
    LevelAltName,
    Tag,
    LevelTagRelation,
    Award,
    AwardAltName,
    AwardTagRelation,
    User,
    StorageStats,
    Skin,
    UsedStats,
    UsedSkin,
    OwnedSkin,
    SkinTagRelation,
    SkinAltName,
]


@listenConsole()
@debugOnly()
@matchLiteral("::dump-pickle")
@withFreeSession()
async def _(session: AsyncSession, ctx: ConsoleContext):
    def asDict(obj: Base):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

    async def sel(cls: type[Base]):
        return list(
            map(lambda x: asDict(x), (await session.execute(select(cls))).scalars())
        )

    output = {}

    for cls in to_pickle_list:
        output[cls.__name__] = await sel(cls)

    with open(os.path.join(".", "data/dumps.pickle"), "wb") as f:
        pickle.dump(output, f)

    await ctx.reply(UniMessage("ok"))


@listenConsole()
@debugOnly()
@matchLiteral("::load-pickle")
async def _(ctx: ConsoleContext):
    with open(os.path.join(".", "data/dumps.pickle"), "rb") as f:
        output: dict[str, list[dict[str, Any]]] = pickle.load(f)

    for cls in to_pickle_list:
        session = get_session()

        async with session.begin():
            await session.execute(delete(cls))
            await session.commit()

    for cls in to_pickle_list:
        session = get_session()
        async with session.begin():
            for obj in output[cls.__name__]:
                session.add(cls(**obj))

            await session.commit()
        await ctx.reply(UniMessage(f"{cls.__name__} ok"))

    await ctx.reply(UniMessage("ok"))


@listenConsole()
@debugOnly()
@matchLiteral("::clear-database")
async def _(ctx: ConsoleContext):
    for cls in to_pickle_list:
        session = get_session()

        async with session.begin():
            await session.execute(delete(cls))
            await session.commit()

    await ctx.reply(UniMessage("ok"))


@listenConsole()
@matchLiteral("::make-backup")
async def _(ctx: ConsoleContext):
    """
    给 SQLITE 数据库备份，只要复制文件即可
    """

    fp = os.path.join(".", "data/db.sqlite3")
    if not os.path.exists(fp):
        await ctx.reply(UniMessage(la.dev.database_not_found))
        return

    with open(fp, "rb") as f:
        data = f.read()

    tp = os.path.join(".", f"data/backup/db-{int(time.time())}.sqlite3")

    with open(tp, "wb") as f:
        f.write(data)

    await ctx.reply(UniMessage("ok"))


def _backup():
    with tarfile.open(f"data/backup/backup-{int(time.time())}.tar.gz", "w:gz") as tar:
        tar.add("data/skins")
        tar.add("data/awards")
        tar.add("data/kagami")
        tar.add("data/db.sqlite3")

        if os.path.exists("data/catch/"):
            tar.add("data/catch")


@listenConsole()
@matchLiteral("::backup-full")
async def _(ctx: ConsoleContext):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _backup)
    await ctx.reply(UniMessage("ok"))
