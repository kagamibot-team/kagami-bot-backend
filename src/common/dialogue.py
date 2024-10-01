"""
维护静态的对话文稿
"""

from enum import Enum
from pathlib import Path

from src.ui.types.liechang import DialogueMessage


class DialogFrom(Enum):
    lqr = Path("./res/dialog/lqr.txt")
    pigeon = Path("./res/dialog/pigeon.txt")


def liechang_handle_single_line(text: str) -> DialogueMessage | None:
    if "：" not in text:
        return None
    first, second = text.split("：", maxsplit=1)
    if " " not in first:
        return None
    speaker, face = first.split(" ", maxsplit=1)
    return DialogueMessage(
        text=second,
        speaker=speaker,
        face=face,
    )


def get_dialog(origin: DialogFrom = DialogFrom.lqr):
    with open(origin.value, "r", encoding="utf-8") as f:
        val = f.readlines()
    val = [liechang_handle_single_line(i) for i in val]
    val = [i for i in val if i is not None]
    return val
