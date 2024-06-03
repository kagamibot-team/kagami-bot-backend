import os
from ..putils import PydanticDataManager, PydanticDataManagerGlobal
from .models import Award, GameGlobalConfig, Level, UserData


userData = PydanticDataManager(
    UserData, os.path.join(os.getcwd(), "data", "catch", "users.json")
)
globalData = PydanticDataManagerGlobal(
    GameGlobalConfig, os.path.join(os.getcwd(), "data", "catch", "global.json")
)


def save():
    clearUnavailableAward()
    ensureNoSameAid()

    userData.save()
    globalData.save()


def ensureNoSameAid():
    with globalData as d:
        awards = d.awards

        d.awards = []

        awardHashmap: set[int] = set()

        for award in awards:
            if award.aid in awardHashmap:
                continue
            
            awardHashmap.add(award.aid)


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

        userData.set(user, uData)


def getAwardByAwardName(name: str):
    return [a for a in globalData.get().awards if a.name == name]

def getLevelByLevelName(name: str):
    return [l for l in globalData.get().levels if l.name == name]


def getAwardsFromLevelId(lid: int):
    return [a for a in getAllAwards() if a.levelId == lid]


def getAllLevels():
    return sorted(globalData.get().levels, key=lambda level: -level.weight)


def getAllAwards():
    return globalData.get().awards


def getWeightSum():
    result = 0

    for level in getAllLevels():
        if len(getAwardsFromLevelId(level.lid)) > 0:
            result += level.weight

    return result


def getPosibilities(level: Level):
    return round(level.weight / getWeightSum() * 100, 2)
