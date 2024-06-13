from nonebot_plugin_alconna import Alconna, Arparma, UniMessage
from arclet.alconna import Arg, ArgFlag
from nonebot_plugin_orm import AsyncSession

from ....models.data import switchSkin

from ....models.crud import getAllOwnedSkin, getAwardByName, getOwnedSkin, getSkinByName, getUsedSkin, getUsedSkinBySkin, getUser, setSkin

from ....events.context import OnebotGroupMessageContext, OnebotPrivateMessageContext
from ....events import root
from ....events.decorator import listenOnebot, matchAlconna, withSessionLock


@listenOnebot(root)
@matchAlconna(
    Alconna(
        "re:(更换|改变|替换|切换)(小哥)?(皮肤)",
        Arg("name", str)
    )
)
@withSessionLock()
async def _(
    ctx: OnebotGroupMessageContext | OnebotPrivateMessageContext,
    session: AsyncSession,
    result: Arparma,
):
    name = result.query[str]("name")
    user = await getUser(session, ctx.getSenderId())

    if name is None:
        return
    
    award = await getAwardByName(session=session, name=name)

    if award is None:
        skin = await getSkinByName(session=session, name=name)
        
        if skin is None:
            await ctx.reply(UniMessage().text(f"你所输入的 {name} 不存在"))
            return
        
        owned = await getOwnedSkin(session, user, skin)
        if owned is None:
            await ctx.reply(UniMessage().text(f"你还没有 {name}"))
            return
        
        used = await getUsedSkinBySkin(session, user, skin)
        if used:
            await session.delete(used)
            await ctx.reply(UniMessage().text(f"已将 {skin.award.name} 的皮肤更换为默认了"))
            await session.commit()
            return

        await setSkin(session, user, skin)
        await ctx.reply(UniMessage().text(f"已经将 {skin.award.name} 的皮肤更改为 {name}"))
        return
    
    skins = await getAllOwnedSkin(session, user, award)
    skin = await switchSkin(session, user, [s.skin for s in skins], award)
    
    if skin is None:
        await ctx.reply(UniMessage().text(f"已经将 {name} 的皮肤更改为默认了"))
    else:
        await ctx.reply(UniMessage().text(f"已将 {name} 的皮肤更换为 {skin.name} 了"))
