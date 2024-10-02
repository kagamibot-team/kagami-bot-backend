"""
维护静态的对话文稿
"""

from enum import Enum
from pathlib import Path

from src.ui.types.liechang import DialogueMessage


class DialogFrom(Enum):
    liechang_normal = Path("./res/dialog/通常_猎场.txt")
    liechang_huaout = Path("./res/dialog/华出_猎场.txt")
    hecheng_normal = Path("./res/dialog/通常_合成部.txt")
    hecheng_huaout = Path("./res/dialog/华出_猎场.txt")


def handle_single_line_dialogue(text: str) -> DialogueMessage | None:
    scene = None
    if "|" in text:
        scene, text = text.split("|", maxsplit=1)
        scene = set(tag for tag in scene.split(",") if len(tag) > 0)
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
        scene=scene,
    )


def get_dialog(
    origin: DialogFrom = DialogFrom.liechang_normal,
    allowed_scene: set[str] | None = None,
) -> list[DialogueMessage]:
    with open(origin.value, "r", encoding="utf-8") as f:
        val = f.readlines()
    val = [handle_single_line_dialogue(i) for i in val]
    val = [i for i in val if i is not None]
    if allowed_scene is not None:
        val = [i for i in val if i.scene is None or len(i.scene & allowed_scene) > 0]
    return val
