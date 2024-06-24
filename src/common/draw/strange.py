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
