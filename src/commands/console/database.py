"""
所有仅在控制台中才能使用的指令
"""

import os
import pickle
import time
from typing import Any
from nonebot_plugin_alconna import UniMessage
from sqlalchemy import delete, select
from ...events.context import ConsoleContext
from ...utils.typing import Session
from ...events import root
from ...events.decorator import listenConsole, matchLiteral, withFreeSession
from models import *


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


@listenConsole(root)
@matchLiteral("::dump-pickle")
@withFreeSession()
async def _(session: Session, ctx: ConsoleContext):
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


@listenConsole(root)
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


@listenConsole(root)
@matchLiteral("::clear-database")
async def _(ctx: ConsoleContext):
    for cls in to_pickle_list:
        session = get_session()

        async with session.begin():
            await session.execute(delete(cls))
            await session.commit()
    
    await ctx.reply(UniMessage("ok"))


@listenConsole(root)
@matchLiteral("::make-backup")
async def _(ctx: ConsoleContext):
    """
    给 SQLITE 数据库备份，只要复制文件即可
    """

    fp = os.path.join(".", "data/db.sqlite3")
    if not os.path.exists(fp):
        await ctx.reply(UniMessage("数据库文件不存在"))
        return

    with open(fp, "rb") as f:
        data = f.read()
    
    tp = os.path.join(".", f"data/backup/db-{int(time.time())}.sqlite3")

    with open(tp, "wb") as f:
        f.write(data)

    await ctx.reply(UniMessage("ok"))
