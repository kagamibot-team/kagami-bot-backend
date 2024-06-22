import asyncio
import os
import random

from src.imports import *


def randomKagami():
    rootPath = os.path.join(".", "data", "kagami")

    if not os.path.exists(rootPath):
        return None
    
    files = os.listdir(rootPath)
    if len(files) == 0:
        return None
    
    return os.path.join(rootPath, random.choice(files))


@listenGroup()
async def ping(ctx: GroupContext):
    if ctx.event.is_tome() and len(await ctx.getMessage()) == 1 and (await ctx.getMessage())[0].data['text'] == '':
        kagami = randomKagami()
        if kagami is None:
            return
        
        await ctx.reply(UniMessage().image(path=kagami))


@listenOnebot()
@matchRegex("^[小|柊]镜[， ,]?跳?科目三$")
@withLoading("")
async def _(ctx: PublicContext, _: Match[str]):
    await asyncio.sleep(5)
