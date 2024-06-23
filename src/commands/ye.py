from src.imports import *


@listenOnebot()
@matchLiteral("哇嘎嘎嘎")
@withSessionLock()
async def _(ctx: OnebotMessageContext, session: AsyncSession):
    uid = await get_uid_by_qqid(session, ctx.getSenderId())

    # 在数据库中，小光和小望的 ID
    guang = 1
    wang = 4

    guang_sto = await get_statistics(session, uid, guang)
    wang_sto = await get_statistics(session, uid, wang)

    if guang_sto > 0 and wang_sto > 0:
        ye_query = select(Skin.data_id).filter(
            Skin.name == "耶", Skin.applied_award_id == 75
        )
        ye = (await session.execute(ye_query)).scalar_one_or_none()

        if ye is None:
            logger.warning("请升级到最新数据库，才有耶皮肤")
            return

        await give_skin(session, uid, ye)
        await session.commit()
