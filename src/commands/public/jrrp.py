from src.imports import *


import random


@listenPublic()
@matchLiteral("小镜jrrp") 
async def _(ctx: PublicContext):
    qqid = ctx.getSenderId()
    dt = now_datetime()

    if qqid is None:
        qqid = 0
    
    random.seed(str(qqid) + "-" + str(dt.date()))
    jrrp = random.randint(1, 100)

    await ctx.reply(UniMessage().text("你的今日人品是：" + str(jrrp)))