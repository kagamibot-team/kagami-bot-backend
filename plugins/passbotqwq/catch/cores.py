from dataclasses import dataclass
import itertools
import random
import time
from .data import getAllAwards, getAllLevelsOfAwardList, getAwardsFromLevelId, userData, globalData
from .models import Award


@dataclass
class Pick:
    awardId: int
    fromNumber: int
    toNumber: int

    def isNew(self):
        return self.fromNumber == 0

    def delta(self):
        return self.toNumber - self.fromNumber


@dataclass
class PicksResult:
    picks: list[Pick]
    uid: int
    restCount: int

    def counts(self):
        return sum([p.delta() for p in self.picks])


def pick(uid: int) -> list[Award]:
    allAvailableLevels = getAllLevelsOfAwardList(getAllAwards())
    level = random.choices(allAvailableLevels, [l.weight for l in allAvailableLevels])[0]
    awards = getAwardsFromLevelId(level.lid)
    return [random.choice(awards)]


def recalcPickTime(uid: int):
    maxPick = globalData.get().maximusPickCache
    timeDelta = globalData.get().timeDelta
    nowTime = time.time()

    with userData.open(uid) as d:
        if timeDelta == 0:
            d.pickCounts = maxPick
            d.pickCalcTime = nowTime
            return -1

        if d.pickCounts >= maxPick:
            d.pickCalcTime = nowTime
            return -1
        
        countAdd = int((nowTime - d.pickCalcTime) / timeDelta)
        d.pickCalcTime += countAdd * timeDelta
        d.pickCounts += countAdd

        if d.pickCounts >= maxPick:
            d.pickCounts = maxPick
            d.pickCalcTime = nowTime
            return -1
        
        return d.pickCounts - nowTime


def canPickCount(uid: int):
    recalcPickTime(uid)
    return userData.get(uid).pickCounts


def handlePick(uid: int, maxPickCount: int = 1) -> PicksResult:
    count = canPickCount(uid)
    if maxPickCount > 0:
        count = min(maxPickCount, count)
    else:
        count = count

    pickResult = PicksResult([], uid, userData.get(uid).pickCounts - count)

    awards = list(itertools.chain(*[pick(uid) for _ in range(count)]))
    awardsDelta: dict[int, int] = {}

    for award in awards:
        if award.aid in awardsDelta.keys():
            awardsDelta[award.aid] += 1
        else:
            awardsDelta[award.aid] = 1
    
    with userData.open(uid) as d:
        d.pickCounts -= count

        for aid in awardsDelta:
            if aid not in d.awardCounter.keys():
                d.awardCounter[aid] = 0
            
            oldValue = d.awardCounter[aid]
            d.awardCounter[aid] += awardsDelta[aid]

            pickResult.picks.append(Pick(aid, oldValue, oldValue + awardsDelta[aid]))
    
    return pickResult
