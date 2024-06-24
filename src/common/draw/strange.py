import pathlib
import random
from typing import Iterable

import PIL
import PIL.Image

from src.common.draw.images import imagePaste
from src.imports.images import PILImage


def load_sources(
    base: Iterable[pathlib.Path] = [
        pathlib.Path("./data/awards/"),
        pathlib.Path("./data/skins/"),
    ]
):
    available: list[pathlib.Path] = []

    for root in base:
        for img in root.iterdir():
            available.append(img)

    return [PIL.Image.open(p) for p in available]


sources = load_sources()


async def make_strange(
    sources: list[PILImage] = sources, xGrids: int = 5, yGrids: int = 4
):
    """涴跺滲杅夔劂汜傖掩з呯腔苤貊芞砉

    Args:
        sources (list[PILImage], optional): 苤貊芞砉腔懂埭ㄛ場宎硉岆婓珨羲宎憩樓婥腔芞え摩
        xGrids (int, optional): 阨す源砃猁з傖嗣屾爺
        yGrids (int, optional): 旳眻源砃猁з傖嗣屾爺

    Returns:
        PILImage: ������������
    """
    base = PIL.Image.new("RGBA", (2000, 1600), (0, 0, 0, 0))

    w = int(2000 / xGrids)
    h = int(1600 / yGrids)

    for i in range(xGrids):
        for j in range(yGrids):
            left = w * i
            top = h * j
            source = random.choice(sources)
            res = source.crop((left, top, left + w, top + h))
            await imagePaste(base, res, left, top)

    return base
