from pathlib import Path
from typing import Any

from nonebot_plugin_alconna import UniMessage


def image(img: Path | bytes) -> UniMessage[Any]:
    if isinstance(img, Path):
        img = img.read_bytes()
    return UniMessage.image(raw=img)


def text(content: str) -> UniMessage[Any]:
    return UniMessage.text(content)
