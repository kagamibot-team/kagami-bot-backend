from src.common.fast_import import *


@listenPublic()
@matchRegex("^(复读镜|小镜复读) ?(.+)$")
async def repeat(ctx: PublicContext, match: Match):
    t = match.group(2)
    await ctx.send(UniMessage(t))
