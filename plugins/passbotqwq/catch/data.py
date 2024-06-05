import base64
import os
from ..putils import PydanticDataManager, PydanticDataManagerGlobal
from .models import Award, GameGlobalConfig, Level, UserData


userData = PydanticDataManager(
    UserData, os.path.join(os.getcwd(), "data", "catch", "users.json")
)
globalData = PydanticDataManagerGlobal(
    GameGlobalConfig, os.path.join(os.getcwd(), "data", "catch", "global.json"),
    os.path.join(os.getcwd(), 'data', 'catch', 'backup')
)


def save():
    clearUnavailableAward()
    ensureNoSameAid()
    ensureNoSameLid()

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
            d.awards.append(award)


def ensureNoSameLid():
    with globalData as d:
        levels = d.levels

        d.levels = []

        awardHashmap: set[int] = set()

        for level in levels:
            if level.lid in awardHashmap:
                continue
            
            awardHashmap.add(level.lid)
            d.levels.append(level)


def getLevelNameOfAward(award: Award):
    return globalData.get().getLevelByLid(award.levelId).name


def getLevelOfAward(award: Award):
    return globalData.get().getLevelByLid(award.levelId)


def clearUnavailableAward():
    for user in userData.data.keys():
        uData = userData.get(user)
        uData.awardCounter = {
            key: uData.awardCounter[key]
            for key in uData.awardCounter.keys()
            if globalData.get().haveAid(key)
        }

        userData.set(user, uData)


def userHaveAward(uid: int, award: Award):
    return len([a for a in getAllAwardsOfOneUser(uid) if a.aid == award.aid])


def getAwardByAwardName(name: str):
    return [a for a in globalData.get().awards if a.name == name]

def getAwardByAwardId(aid: int):
    return [a for a in globalData.get().awards if a.aid == aid][0]

def getLevelByLevelName(name: str):
    return [l for l in globalData.get().levels if l.name == name]


def getAwardsFromLevelId(lid: int):
    return [a for a in getAllAwards() if a.levelId == lid]


def getAllLevels():
    return sorted([l for l in globalData.get().levels if len(getAwardsFromLevelId(l.lid)) > 0], key=lambda level: -level.weight)


def getAllLevelsOfAwardList(awards: list[Award]):
    levels = getAllLevels()

    return [level for level in levels if len([a for a in awards if a.levelId == level.lid]) > 0][::-1]


def getAwardCoundOfOneUser(uid: int, aid: int):
    ac = userData.get(uid).awardCounter

    if aid in ac.keys():
        return ac[aid]
    
    return 0


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


def getImageTarget(award: Award):
    safename = base64.b64encode(award.name.encode()).decode().replace('/', '_').replace('+', '-')
    return os.path.join(os.getcwd(), "data", "catch", "awards", f"{safename}.png")


def _dev_migrate_images():
    with globalData as d:
        for award in d.awards:
            with open(award.imgPath, 'rb') as f:
                raw = f.read()
            
            with open(getImageTarget(award), 'wb') as f:
                f.write(raw)
            
            os.remove(award.imgPath)
            award.updateImage(getImageTarget(award))


def getAllAwardsOfOneUser(uid: int):
    aids: list[Award] = []
    ac = userData.get(uid).awardCounter

    for key in ac.keys():
        if ac[key] <= 0:
            continue

        award = globalData.get().getAwardByAid(key)

        if award is None:
            continue

        aids.append(award)
    
    return aids
