from nonebot import on_message
from nonebot.rule import fullmatch

from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot_plugin_orm import async_scoped_session

from . import models
from .data import pydanticGetAllAwards, pydanticGetAllLevels, userData


dataTransferHandler = on_message(fullmatch("::admin-migrate-database"), priority=10)


@dataTransferHandler.handle()
async def _(session: async_scoped_session, event: GroupMessageEvent):
    if event.sender.user_id != 514827965:
        return

    levels = sorted(pydanticGetAllLevels(), key=lambda l: -l.weight)
    awards = sorted(pydanticGetAllAwards(), key=lambda x: x.aid)
    _userData = userData.data

    _levelMapper = {}
    _awardMapper = {}

    for level in levels:
        dbLevel = models.Level(
            name=level.name,
            weight=level.weight,
        )

        session.add(dbLevel)
        _levelMapper[level.lid] = dbLevel
    
    for award in awards:
        dbAward = models.Award(
            img_path=award.imgPath,
            name=award.name,
            description=award.description,
            level=_levelMapper[award.levelId]
        )

        session.add(dbAward)
        _awardMapper[award.aid] = dbAward
    
    for uid in _userData.keys():
        user = _userData[uid]

        dbUserData = models.UserData(
            qq_id=uid,
            money=user.money,
            pick_count_remain=user.pickCounts,
            pick_count_last_calculated=user.pickCalcTime
        )

        session.add(dbUserData)
    
        for aid in user.awardCounter:
            acount = user.awardCounter[aid]

            dbAwardCountStorage = models.AwardCountStorage(
                target_user = dbUserData,
                target_award = _awardMapper[aid],
                award_count = acount
            )

            session.add(dbAwardCountStorage)
    
    await session.commit()
    await dataTransferHandler.finish(Message(MessageSegment.text("Done")))
