"""
猎场 UI 的数据
"""

import csv
from pathlib import Path
from random import Random

from loguru import logger

from src.ui.types.liechang import DialogueMessage

# 从 CSV 文件中获取数据

DIALOGUES: list[DialogueMessage] = []


with open(Path("./res/dialog/lqr.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        assert len(row) == 3
        DIALOGUES.append(
            DialogueMessage(text=row[2], speaker=row[0].strip(), face=row[1].strip())
        )

logger.info("人 机 一 百 句加载完成")


def get_random_expression(random: Random) -> DialogueMessage:
    return random.choice(DIALOGUES)
