"""
猎场 UI 的数据
"""

from enum import Enum
import csv
from pathlib import Path
from random import Random

from loguru import logger
from pydantic import BaseModel

from src.ui.views.award import InfoView, LevelView
from src.ui.views.user import UserData


class LQRExpressionImage(Enum):
    coming = "我来啦"
    normal = "正常"


class LQRExpression(BaseModel):
    text: str
    face: LQRExpressionImage


# 从 CSV 文件中获取数据

EXPRESSIONS: list[LQRExpression] = []


with open(Path("./res/dialog/lqr.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        assert len(row) == 2
        EXPRESSIONS.append(
            LQRExpression(text=row[1], face=LQRExpressionImage(value=row[0].strip()))
        )

logger.info("人 机 一 百 句加载完成")


class LevelCollectProgress(BaseModel):
    level: LevelView
    collected: int
    sum_up: int


class SinglePackView(BaseModel):
    """
    玩家的其中一个猎场的视图
    """

    pack_id: int
    "猎场的 ID"

    award_count: list[LevelCollectProgress]
    "各个等级，玩家收集了多少小哥，以及各有多少个小哥"

    featured_award: InfoView
    "这个猎场最特色的小哥，用于在界面中展示"

    unlocked: bool
    "用户解锁了这个猎场了么"


def get_random_expression(random: Random) -> LQRExpression:
    return random.choice(EXPRESSIONS)


class PackView(BaseModel):
    """
    玩家的猎场的视图
    """

    packs: list[SinglePackView]
    "所有的猎场"

    user: UserData
    "用户的信息"

    selecting: int
    "用户选择的猎场"

    expression: LQRExpression
    "小鹅表情"

    chips: int
    "有多少薯片？"
