from src.common.get_local_ip import get_ip
from src.imports import *


@listenPublic()
@requireAdmin()
@matchLiteral("::get-ip")
async def _(ctx: PublicContext):
    await ctx.reply("\n".join(get_ip()))
