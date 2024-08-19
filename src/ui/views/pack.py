"""
猎场 UI 的数据
"""

import csv
from pathlib import Path
from random import Random

from loguru import logger
from pydantic import BaseModel

from src.ui.types.liechang import LQRExpression
from src.ui.views.award import LevelView


# 从 CSV 文件中获取数据

EXPRESSIONS: list[LQRExpression] = []


with open(Path("./res/dialog/lqr.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        assert len(row) == 2
        EXPRESSIONS.append(LQRExpression(text=row[1], face=row[0].strip()))

logger.info("人 机 一 百 句加载完成")


class LevelCollectProgress(BaseModel):
    level: LevelView
    collected: int
    sum_up: int


def get_random_expression(random: Random) -> LQRExpression:
    return random.choice(EXPRESSIONS)
