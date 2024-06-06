import base64
from dataclasses import dataclass
import os
from typing import Any, Callable, Generic, TypeVar
from typing_extensions import deprecated
from ..putils import PydanticDataManager, PydanticDataManagerGlobal
from .models import Award, GameGlobalConfig, Level, UserData


class AwardList(list[Award]):
    def aid(self):
        return [a.aid for a in self]
    
    def len(self):
        return len(self)
    
    def name(self):
        return [a.name for a in self]


class LevelList(list[Level]):
    def lid(self):
        return [l.lid for l in self]
    
    def len(self):
        return len(self)


T = TypeVar('T')

class ListFilter(Generic[T]):
    def __init__(self, ls: list[T]) -> None:
        self.ls = ls
        self.limitations: list[Callable[[T], bool]] = []
    
    def _limit(self, limit: Callable[[T], bool]):
        self.limitations.append(limit)
        return self
    
    def get(self) -> list[T]:
        result = self.ls

        for limit in self.limitations:
            result = [v for v in result if limit(v)]
        
        return result
    
    def __call__(self):
        return self.get()


class DBAward(ListFilter[Award]):
    def __init__(self) -> None:
        super().__init__(getAllAwards())
    
    def lid(self, lid: int):
        return self._limit(lambda a: a.levelId == lid)

    def userHave(self, uid: int, atLeast: int = 1):
        return self._limit(lambda a: a.aid in getUserAwardCounter(uid).keys() and getUserAwardCounter(uid)[a.aid] >= atLeast)
    
    def name(self, name: str):
        return self._limit(lambda a: a.name == name)
    
    def aid(self, aid: int):
        return self._limit(lambda a: a.aid == aid)

    def description(self, desc: str = "这只小哥还没有描述，它只是静静地躺在这里，等待着别人给他下定义。"):
        return self._limit(lambda a: a.description == desc)
    
    def get(self):
        return AwardList(super().get())


class DBLevel(ListFilter[Level]):
    def __init__(self) -> None:
        super().__init__(getAllLevels())

    def lid(self, lid: int):
        return self._limit(lambda l: l.lid == lid)
    
    def _weight(self, weightLimiter: Callable[[float], bool]):
        return self._limit(lambda l: weightLimiter(l.weight))
    
    def weightBiggerThan(self, weight: float = 0):
        return self._weight(lambda w: w > weight)
    
    def weightSmallerThan(self, weight: float = 0):
        return self._weight(lambda w: w < weight)
    
    def weightNotBiggerThan(self, weight: float = 0):
        return self._weight(lambda w: w <= weight)
    
    def weightNotSmallerThan(self, weight: float = 0):
        return self._weight(lambda w: w >= weight)
    
    def containAward(self, award: Award):
        return self._limit(lambda l: award.levelId == l.lid)

    def name(self, name: str):
        return self._limit(lambda l: l.name == name)
    
    def get(self):
        return LevelList(super().get())


def save():
    clearUnavailableAward()
    ensureNoSameAid()
    ensureNoSameLid()

    userData.save()
    globalData.save()


def getAllAwards():
    return AwardList(globalData.get().awards)


def getAllLevels():
    return LevelList(globalData.get().levels)


def getUserAwardCounter(uid: int):
    return userData.get(uid).awardCounter


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


@deprecated('该方法将在未来移除，请使用 Filter 替代')
def getAwardByAwardName(name: str):
    return [a for a in globalData.get().awards if a.name == name]


@deprecated('该方法将在未来移除，请使用 Filter 替代')
def getAwardByAwardId(aid: int):
    return [a for a in globalData.get().awards if a.aid == aid][0]


@deprecated('该方法将在未来移除，请使用 Filter 替代')
def getLevelByLevelName(name: str):
    return [l for l in globalData.get().levels if l.name == name]


@deprecated('该方法将在未来移除，请使用 Filter 替代')
def getAwardsFromLevelId(lid: int):
    return [a for a in getAllAwards() if a.levelId == lid]


@deprecated('该方法将在未来移除，请使用 Filter 替代')
def getAllLevelsOfAwardList(awards: list[Award]):
    levels = getAllLevels()

    return [level for level in levels if len([a for a in awards if a.levelId == level.lid]) > 0][::-1]


def getAwardCountOfOneUser(uid: int, aid: int):
    ac = userData.get(uid).awardCounter

    if aid in ac.keys():
        return ac[aid]
    
    return 0



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

    uIndex: int = 0

    def _path():
        return os.path.join(".", "data", "catch", "awards", f"{safename}_{uIndex}.png")

    while os.path.exists(_path()):
        uIndex += 1

    return _path()


@deprecated('该方法将在未来移除，请使用 Filter 替代')
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


userData = PydanticDataManager(
    UserData, os.path.join(".", "data", "catch", "users.json")
)
globalData = PydanticDataManagerGlobal(
    GameGlobalConfig, os.path.join(".", "data", "catch", "global.json"),
    ""
)
