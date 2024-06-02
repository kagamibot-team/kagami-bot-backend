import os
from ..putils import PydanticDataManager, PydanticDataManagerGlobal
from .models import Award, GameGlobalConfig, UserData


userData = PydanticDataManager(
    UserData, os.path.join(os.getcwd(), "data", "catch", "users.json")
)
globalData = PydanticDataManagerGlobal(
    GameGlobalConfig, os.path.join(os.getcwd(), "data", "catch", "global.json")
)


def save():
    clearUnavailableAward()

    userData.save()
    globalData.save()


def getLevelNameOfAward(award: Award):
    return globalData.get().getLevelByLid(award.levelId).name


def clearUnavailableAward():
    for user in userData.data.keys():
        uData = userData.get(user)
        uData.awardCounter = {
            key: uData.awardCounter[key]
            for key in uData.awardCounter.keys()
            if globalData.get().haveAid(key)
        }


def getAwardByAwardName(name: str):
    return [a for a in globalData.get().awards if a.name == name]
