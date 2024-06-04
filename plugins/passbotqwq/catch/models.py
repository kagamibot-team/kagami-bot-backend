import os
import random
from pydantic import BaseModel, Field


DEFAULT_IMG = os.path.join(os.getcwd(), "res", "catch", "default.png")
DEFAULT_BG = os.path.join(os.getcwd(), "res", "catch", "default-bg.png")


class Level(BaseModel):
    lid: int = -1
    name: str = "未命名等级"
    weight: float = 1
    hue: float = 0
    prise: float = 0


class Award(BaseModel):
    aid: int = -1
    imgPath: str = DEFAULT_IMG
    name: str = "名称已丢失"
    description: str = "这只小哥还没有描述，它只是静静地躺在这里，等待着别人给他下定义。"
    levelId: int = -1

    def updateImage(self, img: str):
        if os.path.exists(img):
            self.imgPath = img
        else:
            self.imgPath = DEFAULT_IMG


class GameGlobalConfig(BaseModel):
    levels: list[Level] = Field(default_factory=lambda: [])
    awards: list[Award] = Field(default_factory=lambda: [])
    lidMax: int = 0
    aidMax: int = 0

    timeDelta: float = 3600

    def addLevel(self, name: str, weight: float, prise: float, hue: float):
        self.levels.append(Level(lid=self.lidMax, name=name, weight=weight, hue=hue, prise=prise))
        self.lidMax += 1
        return self.lidMax - 1

    def addAward(self, name: str, lid: int, imgPath: str):
        self.awards.append(
            Award(aid=self.aidMax, imgPath=imgPath, name=name, levelId=lid)
        )

        self.aidMax += 1
        return self.aidMax - 1
    

    def getLevelByLid(self, lid: int):
        levelFiltered = [level for level in self.levels if level.lid == lid]

        if len(levelFiltered) > 0:
            return levelFiltered[0]

        newOne = Level(lid=lid)
        self.levels.append(newOne)

        if self.lidMax <= lid:
            self.lidMax = lid + 1

        return newOne

    def getAwardByAid(self, aid: int):
        awardFiltered = [award for award in self.awards if award.aid == aid]

        if len(awardFiltered) > 0:
            return awardFiltered[0]

        return None
    
    def getAwardByAidStrong(self, aid: int):
        award = self.getAwardByAid(aid)
        assert award != None
        return award
    
    def haveAid(self, aid: int):
        return self.getAwardByAid(aid) != None

    def getAwardsByLevel(self, lid: int):
        return [award for award in self.awards if award.levelId == lid]

    def getAllAvailableLevel(self):
        return [
            level for level in self.levels if len(self.getAwardsByLevel(level.lid)) > 0
        ]

    def pick(self):
        if len(self.awards) == 0:
            raise NotImplementedError

        levels = self.getAllAvailableLevel()
        level = random.choices(levels, [level.weight for level in levels])[0]

        return random.choice(self.getAwardsByLevel(level.lid))

    def containAwardName(self, name: str):
        return len([award for award in self.awards if award.name == name]) > 0

    def isLevelIdExists(self, levelId: int):
        return len([level for level in self.levels if level.lid == levelId]) > 0

    def removeAwardsByName(self, name: str):
        removed = [a for a in self.awards if a.name == name]
        self.awards = [a for a in self.awards if a.name != name]
        return removed
    
    def removeLevelByName(self, name: str):
        removed = [l for l in self.levels if l.name == name]
        self.levels = [l for l in self.levels if l.name != name]
        return removed


class UserData(BaseModel):
    lastCatch: float = 0
    awardCounter: dict[int, int] = Field(default_factory=lambda: {})
    backgroundImage: str = DEFAULT_BG
    money: float = 0

    def addAward(self, aid: int):
        if aid in self.awardCounter.keys():
            self.awardCounter[aid] += 1
        else:
            self.awardCounter[aid] = 1

        return self

    def updateBackground(self, img: str):
        if os.path.exists(img):
            self.backgroundImage = img
        else:
            self.backgroundImage = DEFAULT_BG

    def getAwardSum(self):
        return sum([self.awardCounter[a] for a in self.awardCounter.keys()])
